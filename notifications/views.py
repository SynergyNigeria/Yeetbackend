from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification, PushSubscription
from .serializers import NotificationSerializer, PushSubscriptionSerializer
from pywebpush import webpush, WebPushException
import json
from django.conf import settings

class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for notifications
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_active=True)

class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update notification"""
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        # Mark as read when updating
        serializer.save(is_read=True)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read_view(request):
    """Mark all notifications as read"""
    
    Notification.objects.filter(
        user=request.user,
        is_read=False,
        is_active=True
    ).update(is_read=True)
    
    return Response({'message': 'All notifications marked as read'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count_view(request):
    """Get count of unread notifications"""
    
    count = Notification.objects.filter(
        user=request.user,
        is_read=False,
        is_active=True
    ).count()
    
    return Response({'count': count})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read_view(request, pk):
    """Mark a specific notification as read"""
    
    try:
        notification = Notification.objects.get(
            pk=pk,
            user=request.user,
            is_active=True
        )
        notification.is_read = True
        notification.save()
        
        return Response({'message': 'Notification marked as read'})
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

# Push Notification Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_push_view(request):
    """Subscribe to push notifications"""
    
    subscription_info = request.data.get('subscription')
    user_agent = request.data.get('user_agent', '')
    
    if not subscription_info:
        return Response(
            {'error': 'Subscription data is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create or update subscription
    subscription, created = PushSubscription.objects.update_or_create(
        user=request.user,
        subscription_info=subscription_info,
        defaults={
            'user_agent': user_agent,
            'is_active': True
        }
    )
    
    serializer = PushSubscriptionSerializer(subscription)
    
    return Response({
        'message': 'Successfully subscribed to push notifications',
        'subscription': serializer.data
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_push_view(request):
    """Unsubscribe from push notifications"""
    
    subscription_info = request.data.get('subscription')
    
    if not subscription_info:
        # If no specific subscription provided, deactivate all for this user
        PushSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        return Response({'message': 'All subscriptions deactivated'})
    
    # Deactivate specific subscription
    updated = PushSubscription.objects.filter(
        user=request.user,
        subscription_info=subscription_info,
        is_active=True
    ).update(is_active=False)
    
    if updated:
        return Response({'message': 'Successfully unsubscribed'})
    else:
        return Response(
            {'error': 'Subscription not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def push_subscription_status_view(request):
    """Get push notification subscription status"""
    
    subscriptions = PushSubscription.objects.filter(
        user=request.user,
        is_active=True
    )
    
    serializer = PushSubscriptionSerializer(subscriptions, many=True)
    
    return Response({
        'is_subscribed': subscriptions.exists(),
        'subscriptions': serializer.data
    })

# Utility function to send push notifications
def send_push_notification(user, title, message, notification_type='info', data=None):
    """Send push notification to user's subscribed devices"""
    
    # Get VAPID keys from settings
    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
    vapid_claims = getattr(settings, 'VAPID_CLAIMS', {})
    
    if not vapid_private_key or not vapid_public_key:
        print("VAPID keys not configured")
        return
    
    # Get active subscriptions for user
    subscriptions = PushSubscription.objects.filter(
        user=user,
        is_active=True
    )
    
    if not subscriptions.exists():
        return
    
    # Prepare notification payload
    payload = {
        'title': title,
        'body': message,
        'icon': '/icons/icon-192x192.png',
        'badge': '/icons/badge-72x72.png',
        'data': {
            'type': notification_type,
            'url': '/',
            **(data or {})
        }
    }
    
    # Send to each subscription
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription.subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims={
                    **vapid_claims,
                    'sub': f'mailto:{vapid_claims.get("sub", "admin@yeetbank.com")}'
                }
            )
        except WebPushException as e:
            print(f"Push notification failed: {e}")
            # If subscription is invalid, mark as inactive
            if e.response and e.response.status_code in [404, 410]:
                subscription.is_active = False
                subscription.save()
        except Exception as e:
            print(f"Unexpected error sending push notification: {e}")
