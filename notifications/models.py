from django.db import models
from django.utils import timezone
from django.conf import settings
import json

class Notification(models.Model):
    """Model for user notifications"""
    
    NOTIFICATION_TYPES = [
        ('TRANSACTION', 'Transaction'),
        ('SECURITY', 'Security'),
        ('SYSTEM', 'System'),
        ('PROMOTION', 'Promotion'),
        ('WELCOME', 'Welcome'),
        ('ACCOUNT', 'Account'),
    ]
    
    # Notification details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Related objects (optional)
    transaction = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']


class PushSubscription(models.Model):
    """Model for storing Web Push notification subscriptions"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='push_subscriptions'
    )
    
    # Push subscription details (stored as JSON)
    subscription_info = models.JSONField()
    
    # Device/browser info (optional)
    user_agent = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Push subscription for {self.user.username}"
    
    def get_subscription_info(self):
        """Get subscription info as dict"""
        if isinstance(self.subscription_info, str):
            return json.loads(self.subscription_info)
        return self.subscription_info
    
    class Meta:
        ordering = ['-created_at']
        # Unique constraint to prevent duplicate subscriptions
        unique_together = [['user', 'subscription_info']]
