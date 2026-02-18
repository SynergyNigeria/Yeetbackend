from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, SendMessageView, GetMessagesView

# Create router for viewsets
router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Legacy endpoints for backward compatibility
    path('conversations/', ChatRoomViewSet.as_view({'get': 'conversations'}), name='chat-conversations'),
    path('send-message/', SendMessageView.as_view(), name='chat-send-message'),
    path('messages/<uuid:chat_id>/', GetMessagesView.as_view(), name='chat-messages'),
    
    # New endpoints
    path('support/', ChatRoomViewSet.as_view({'post': 'start_support_chat'}), name='start-support-chat'),
]
