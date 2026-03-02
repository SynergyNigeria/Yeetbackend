from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender='accounts.User')
def create_welcome_notifications(sender, instance, created, **kwargs):
    """Create welcome notifications and send welcome email for new users"""
    
    if created:
        # Import here to avoid app registry issues
        from .models import Notification
        
        # Welcome notification
        Notification.objects.create(
            user=instance,
            title='🎉 Welcome to YEET Bank!',
            message=f'Hi {instance.first_name}! Welcome to YEET Bank. Your account {instance.account_number} is ready for secure banking.',
            notification_type='WELCOME'
        )
        
        # Transfer PIN setup reminder
        Notification.objects.create(
            user=instance,
            title='🔒 Set Up Your Transfer PIN',
            message='For your security, please set up a 4-digit transfer PIN. Go to Settings > Change PIN to create your PIN.',
            notification_type='SECURITY'
        )
        
        # Deposit encouragement
        Notification.objects.create(
            user=instance,
            title='💰 Ready to Get Started?',
            message='Your account is set up and ready! Add money to start sending and receiving with YEET Bank. Tap "Add Money" on your dashboard.',
            notification_type='ACCOUNT'
        )

        # Send welcome email
        try:
            from accounts.email_utils import send_welcome_email
            send_welcome_email(instance)
        except Exception:
            pass  # Email failure must never block registration

@receiver(post_save, sender='transactions.Transaction')
def create_transaction_notification(sender, instance, created, **kwargs):
    """Create notification when transaction is completed"""
    
    # Import here to avoid app registry issues
    from .models import Notification
    from transactions.models import Transaction
    
    if created and instance.status == 'COMPLETED':
        # Create notification for sender
        Notification.objects.create(
            user=instance.sender,
            title='💸 Transaction Completed',
            message=f'Your {instance.transaction_type.lower()} of ${instance.amount} has been processed.',
            notification_type='TRANSACTION',
            transaction=instance
        )
        
        # Create notification for recipient if it's a transfer
        if instance.transaction_type == 'TRANSFER' and instance.recipient:
            Notification.objects.create(
                user=instance.recipient,
                title='💰 Money Received',
                message=f'You received ${instance.amount} from {instance.sender.get_full_name()}.',
                notification_type='TRANSACTION',
                transaction=instance
            )

@receiver(post_save, sender='notifications.Notification')
def send_push_on_notification(sender, instance, created, **kwargs):
    """Send push notification when a new notification is created"""
    
    if created:
        # Import here to avoid circular imports
        from .views import send_push_notification
        
        # Send push notification
        send_push_notification(
            user=instance.user,
            title=instance.title,
            message=instance.message,
            notification_type=instance.notification_type,
            data={
                'notification_id': instance.id,
                'transaction_id': instance.transaction_id if instance.transaction else None
            }
        )