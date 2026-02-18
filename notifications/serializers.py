from rest_framework import serializers
from .models import Notification, PushSubscription

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'is_read', 'is_active', 'created_at', 'transaction'
        ]
        read_only_fields = ['id', 'created_at']

class PushSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Push Subscription"""
    
    class Meta:
        model = PushSubscription
        fields = ['id', 'subscription_info', 'user_agent', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']