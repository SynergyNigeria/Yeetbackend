from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage, ChatRoomMembership

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for chat"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff']
        read_only_fields = ['id', 'username', 'email', 'is_staff']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['full_name'] = instance.get_full_name() or instance.username
        data['avatar'] = self.get_avatar(instance)
        return data
    
    def get_avatar(self, obj):
        """Generate avatar initials"""
        full_name = obj.get_full_name()
        if full_name:
            names = full_name.split()
            if len(names) >= 2:
                return f"{names[0][0]}{names[1][0]}".upper()
            else:
                return names[0][:2].upper()
        return obj.username[:2].upper()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Chat message serializer"""
    
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'content', 'message_type', 'image', 'file',
            'sender', 'sender_id', 'created_at', 'is_edited', 'edited_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_edited', 'edited_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format time for frontend
        if instance.created_at:
            data['time'] = instance.created_at.strftime('%I:%M %p')
        
        # Ensure full URL for image if present
        if instance.image and hasattr(instance.image, 'url'):
            request = self.context.get('request')
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
        
        return data


class ChatRoomSerializer(serializers.ModelSerializer):
    """Chat room serializer"""
    
    participants = UserSerializer(many=True, read_only=True)
    last_message = ChatMessageSerializer(source='get_last_message', read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'participants', 'last_message',
            'unread_count', 'is_active', 'created_at', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']
    
    def get_unread_count(self, obj):
        """Get unread count for the requesting user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_unread_count(request.user)
        return 0
    
    def to_representation(self, instance):
        data = super().to_representation(instance) 
        # For support chats, set display name based on participant
        if instance.room_type == 'USER_SUPPORT':
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                other_users = instance.participants.exclude(id=request.user.id)
                if other_users.exists():
                    other_user = other_users.first()
                    if other_user.is_staff or other_user.is_superuser:
                        data['display_name'] = 'Support Agent'
                        data['avatar'] = 'SA'
                        data['is_online'] = True  # Assume support is always online
                    else:
                        data['display_name'] = other_user.get_full_name() or other_user.username
                        data['avatar'] = UserSerializer().get_avatar(other_user)
                        data['is_online'] = False  # Could implement real online status
                else:
                    data['display_name'] = 'Support Chat'
                    data['avatar'] = 'SC'
                    data['is_online'] = True
            else:
                data['display_name'] = instance.name or 'Support Chat'
                data['avatar'] = 'SC'
                data['is_online'] = True
        else:
            data['display_name'] = instance.name
            data['avatar'] = 'GC'
            data['is_online'] = False
        
        # Format last activity time
        if instance.last_activity:
            from django.utils import timezone
            now = timezone.now()
            diff = now - instance.last_activity
            
            if diff.days > 0:
                data['last_activity_display'] = f"{diff.days}d ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                data['last_activity_display'] = f"{hours}h ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                data['last_activity_display'] = f"{minutes}m ago"
            else:
                data['last_activity_display'] = "Just now"
        else:
            data['last_activity_display'] = "Now"
        
        return data


class CreateMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""
    
    content = serializers.CharField(required=False, allow_blank=True)
    message_type = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    file = serializers.FileField(required=False)
    
    class Meta:
        model = ChatMessage
        fields = ['content', 'message_type', 'image', 'file']
    
    def validate(self, data):
        # Set default message type if not provided
        if not data.get('message_type'):
            if data.get('image'):
                data['message_type'] = 'IMAGE'
            elif data.get('file'):
                data['message_type'] = 'FILE'
            else:
                data['message_type'] = 'TEXT'
        
        # Set default content if not provided
        if not data.get('content'):
            if data.get('image'):
                data['content'] = 'Photo'
            elif data.get('file'):
                data['content'] = 'File'
            else:
                data['content'] = ''
        
        return data
    
    def create(self, validated_data):
        room_id = self.context.get('room_id')
        room = ChatRoom.objects.get(id=room_id)
        user = self.context['request'].user
        
        # Ensure user is participant in the room
        if not room.participants.filter(id=user.id).exists():
            raise serializers.ValidationError("You are not a participant in this chat room.")
        
        message = ChatMessage.objects.create(
            room=room,
            sender=user,
            **validated_data
        )
        
        return message
