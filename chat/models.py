from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid


class ChatRoom(models.Model):
    """Chat room model for user conversations"""
    
    ROOM_TYPES = [
        ('USER_SUPPORT', 'User to Support'),
        ('USER_USER', 'User to User'),
        ('GROUP', 'Group Chat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='USER_SUPPORT')
    
    # Participants
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        if self.name:
            return self.name
        participants_names = ', '.join([p.get_full_name() or p.username for p in self.participants.all()[:2]])
        return f"Chat: {participants_names}"
    
    def get_last_message(self):
        """Get the most recent message in this room"""
        return self.messages.filter(is_active=True).first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        last_read = ChatRoomMembership.objects.filter(
            room=self, user=user
        ).first()
        
        if last_read and last_read.last_read_message:
            return self.messages.filter(
                created_at__gt=last_read.last_read_message.created_at,
                is_active=True
            ).exclude(sender=user).count()
        else:
            return self.messages.exclude(sender=user).filter(is_active=True).count()


class ChatMessage(models.Model):
    """Chat message model"""
    
    MESSAGE_TYPES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('FILE', 'File'),
        ('SYSTEM', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='TEXT')
    content = models.TextField(blank=True)
    
    # Media attachments
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update room's last activity
        self.room.last_activity = self.created_at
        self.room.save(update_fields=['last_activity'])


class ChatRoomMembership(models.Model):
    """Track user membership and read status in chat rooms"""
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_memberships')
    
    # Read status
    last_read_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, blank=True, null=True)
    last_read_at = models.DateTimeField(blank=True, null=True)
    
    # Membership status
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Notifications
    notifications_enabled = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.room}"
    
    def mark_as_read(self, message=None):
        """Mark room as read up to a specific message"""
        if message is None:
            message = self.room.get_last_message()
        
        if message:
            self.last_read_message = message
            self.last_read_at = timezone.now()
            self.save()
