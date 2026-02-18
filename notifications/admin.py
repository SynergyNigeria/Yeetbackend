from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'notification_type', 'is_read', 'is_active', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__account_number', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read', 'is_active')
        }),
        ('Related', {
            'fields': ('transaction',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
