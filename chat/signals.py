from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage, ChatRoomMembership
from notifications.models import Notification

User = get_user_model()


@receiver(m2m_changed, sender=ChatRoom.participants.through)
def create_chat_memberships(sender, instance, action, pk_set, **kwargs):
    """Create ChatRoomMembership objects when participants are added to a room"""
    if action == 'post_add':
        for user_id in pk_set:
            user = User.objects.get(id=user_id)
            ChatRoomMembership.objects.get_or_create(
                room=instance,
                user=user,
                defaults={
                    'is_admin': user.is_staff or user.is_superuser,
                    'notifications_enabled': True
                }
            )


@receiver(post_save, sender=ChatMessage)
def handle_new_message(sender, instance, created, **kwargs):
    """Handle new chat message - create notifications"""
    if created:
        # Get all participants except the sender
        participants = instance.room.participants.exclude(id=instance.sender.id)
        
        # Create notifications for all other participants
        for participant in participants:
            # Check if user has notifications enabled for this room
            membership = ChatRoomMembership.objects.filter(
                room=instance.room,
                user=participant,
                notifications_enabled=True
            ).first()
            
            if membership:
                # Create notification
                notification_title = '💬 New Message'
                if instance.room.room_type == 'USER_SUPPORT':
                    if instance.sender.is_staff or instance.sender.is_superuser:
                        notification_title = '💬 Support Reply'
                    else:
                        notification_title = '💬 New Support Message'
                
                # Truncate message content for notification
                message_preview = instance.content[:50] + ('...' if len(instance.content) > 50 else '')
                
                Notification.objects.create(
                    user=participant,
                    title=notification_title,
                    message=f'{instance.sender.get_full_name()}: {message_preview}',
                    notification_type='SYSTEM',
                )

