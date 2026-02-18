from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from .models import ChatRoom, ChatMessage, ChatRoomMembership
from .serializers import (
    ChatRoomSerializer,
    ChatMessageSerializer, 
    CreateMessageSerializer
)

User = get_user_model()


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat rooms"""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get chat rooms where user is a participant"""
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True
        ).distinct()
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific chat room"""
        room = get_object_or_404(ChatRoom, id=pk, participants=request.user)
        
        # Mark as read
        membership = ChatRoomMembership.objects.filter(
            room=room,
            user=request.user
        ).first()
        
        if membership:
            membership.mark_as_read()
        
        # Get messages
        messages = ChatMessage.objects.filter(
            room=room,
            is_active=True
        ).order_by('created_at')  # Oldest first for display
        
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a chat room"""
        room = get_object_or_404(ChatRoom, id=pk, participants=request.user)
        
        serializer = CreateMessageSerializer(
            data=request.data,
            context={'request': request, 'room_id': room.id}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            response_serializer = ChatMessageSerializer(message, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get all conversations for the user (legacy endpoint)"""
        rooms = self.get_queryset()
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def start_support_chat(self, request):
        """Start a new support chat or get existing one"""
        user = request.user
        
        # Look for existing support chat
        support_room = ChatRoom.objects.filter(
            participants=user,
            room_type='USER_SUPPORT',
            is_active=True
        ).first()
        
        if support_room:
            serializer = self.get_serializer(support_room)
            return Response(serializer.data)
        
        # Create new support chat
        support_users = User.objects.filter(is_staff=True)
        if not support_users.exists():
            return Response(
                {'error': 'No support agents available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        support_user = support_users.first()
        
        room = ChatRoom.objects.create(
            name=f'Support Chat - {user.get_full_name() or user.username}',
            room_type='USER_SUPPORT'
        )
        
        room.participants.add(user, support_user)
        
        # Send welcome message
        ChatMessage.objects.create(
            room=room,
            sender=support_user,
            content='Hello! How can I help you today?',
            message_type='TEXT'
        )
        
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def staff_users(self, request):
        """Get all staff users for chat"""
        staff_users = User.objects.filter(is_staff=True).values(
            'id', 'username', 'first_name', 'last_name', 'email'
        )
        return Response(list(staff_users))
    
    @action(detail=False, methods=['post'])
    def start_chat_with_user(self, request):
        """Start a chat with a specific staff user"""
        target_user_id = request.data.get('user_id')
        if not target_user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_user = User.objects.get(id=target_user_id, is_staff=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Staff user not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        
        # Check for existing chat room between these users
        existing_room = ChatRoom.objects.filter(
            participants=user
        ).filter(
            participants=target_user
        ).filter(
            room_type='USER_USER',
            is_active=True
        ).first()
        
        if existing_room:
            serializer = self.get_serializer(existing_room)
            return Response(serializer.data)
        
        # Create new chat room
        room = ChatRoom.objects.create(
            name=f'Chat with {target_user.get_full_name() or target_user.username}',
            room_type='USER_USER'
        )
        
        room.participants.add(user, target_user)
        
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def set_typing(self, request, pk=None):
        """Set typing status for a user in a chat room"""
        room = get_object_or_404(ChatRoom, id=pk, participants=request.user)
        is_typing = request.data.get('is_typing', False)
        
        # Store typing status in cache with 3 second expiry
        cache_key = f'typing_{room.id}_{request.user.id}'
        if is_typing:
            cache.set(cache_key, True, 3)  # Expires in 3 seconds
        else:
            cache.delete(cache_key)
        
        return Response({'status': 'ok'})
    
    @action(detail=True, methods=['get'])
    def get_typing(self, request, pk=None):
        """Get typing status of other users in the chat room"""
        room = get_object_or_404(ChatRoom, id=pk, participants=request.user)
        
        # Check if any other participant is typing
        other_participants = room.participants.exclude(id=request.user.id)
        typing_users = []
        
        for participant in other_participants:
            cache_key = f'typing_{room.id}_{participant.id}'
            if cache.get(cache_key):
                typing_users.append({
                    'id': participant.id,
                    'name': participant.get_full_name() or participant.username
                })
        
        return Response({
            'is_typing': len(typing_users) > 0,
            'typing_users': typing_users
        })


class SendMessageView(generics.CreateAPIView):
    """Legacy endpoint for sending messages"""
    
    serializer_class = CreateMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Handle legacy format
        data = request.data.copy()
        
        # Convert chat_id to room_id if present
        if 'chat_id' in data:
            data['room_id'] = data.pop('chat_id')
        
        # Handle message field
        if 'message' in data:
            data['content'] = data.pop('message')
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            message = serializer.save()
            response_serializer = ChatMessageSerializer(message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMessagesView(generics.ListAPIView):
    """Legacy endpoint for getting messages"""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        room = get_object_or_404(ChatRoom, id=chat_id, participants=self.request.user)
        
        # Mark as read
        membership = ChatRoomMembership.objects.filter(
            room=room,
            user=self.request.user
        ).first()
        
        if membership:
            membership.mark_as_read()
        
        return ChatMessage.objects.filter(
            room=room,
            is_active=True
        ).order_by('created_at')
