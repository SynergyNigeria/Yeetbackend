from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatRoomMembership


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'room_type', 'participant_count', 'is_active', 'created_at', 'last_activity']
    list_filter = ['room_type', 'is_active', 'created_at']
    filter_horizontal = ['participants']
    search_fields = ['name', 'participants__username', 'participants__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_activity']
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'content_preview', 'created_at', 'is_active']
    list_filter = ['message_type', 'is_active', 'created_at', 'room__room_type']
    search_fields = ['content', 'sender__username', 'sender__email']
    readonly_fields = ['id', 'created_at', 'edited_at']
    raw_id_fields = ['room', 'sender']
    
    def content_preview(self, obj):
        if obj.message_type == 'IMAGE':
            return '📷 Image'
        elif obj.message_type == 'FILE':
            return '📎 File'
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'


@admin.register(ChatRoomMembership)
class ChatRoomMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'is_admin', 'is_active', 'joined_at', 'last_read_at']
    list_filter = ['is_admin', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__email', 'room__name']
    raw_id_fields = ['room', 'user', 'last_read_message']
    readonly_fields = ['joined_at']
