from django.contrib import admin
from .models import Transaction, TransactionReport

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('sender__email', 'recipient__email', 'sender__account_number', 'recipient__account_number', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'transaction_id', 'created_at', 'completed_at')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_id', 'sender', 'recipient', 'recipient_account', 'amount', 'transaction_type', 'description')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        })
    )


@admin.register(TransactionReport)
class TransactionReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'transaction', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('reporter__email', 'transaction__transaction_id', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'resolved_at')
    
    fieldsets = (
        ('Report Details', {
            'fields': ('transaction', 'reporter', 'reason', 'description')
        }),
        ('Status & Resolution', {
            'fields': ('status', 'admin_notes', 'resolution')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        })
    )
