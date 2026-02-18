import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                f'notifications_{self.user.id}',
                self.channel_name
            )
            await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f'notifications_{self.user.id}',
                self.channel_name
            )
    
    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass
    
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        notification = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': notification
        }))