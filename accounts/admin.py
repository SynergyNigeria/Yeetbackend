from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'account_number', 
        'balance', 'is_verified', 'has_deposit', 'account_level_display', 
        'is_prime', 'has_set_transfer_pin'
    )
    
    list_filter = (
        'is_verified', 'has_deposit', 'is_basic', 'is_premium', 
        'is_business', 'is_prime', 'has_set_transfer_pin', 
        'is_staff', 'is_active', 'date_joined'
    )
    
    search_fields = ('username', 'email', 'first_name', 'last_name', 'account_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Banking Information', {
            'fields': (
                'phone', 'country', 'residential_address', 'account_number', 
                'balance', 'transfer_pin', 'has_set_transfer_pin'
            )
        }),
        ('Account Verification & Tiers', {
            'fields': (
                'is_verified', 'has_deposit', 'is_basic', 'is_premium', 
                'is_business', 'is_prime'
            ),
            'description': 'Banking verification levels. Prime accounts bypass most restrictions.'
        }),
    )
    
    readonly_fields = ('account_number', 'has_set_transfer_pin')
    
    def account_level_display(self, obj):
        """Display account level in admin list"""
        return obj.get_account_level()
    account_level_display.short_description = 'Account Level'
    
    actions = ['make_verified', 'make_prime', 'add_deposit_flag', 'reset_to_basic']
    
    def make_verified(self, request, queryset):
        """Mark selected users as verified"""
        count = queryset.update(is_verified=True)
        self.message_user(request, f'{count} users marked as verified.')
    make_verified.short_description = "✓ Mark as verified"
    
    def make_prime(self, request, queryset):
        """Upgrade selected users to Prime (full privileges)"""
        count = queryset.update(is_prime=True, is_verified=True, has_deposit=True)
        self.message_user(request, f'{count} users upgraded to Prime.')
    make_prime.short_description = "⭐ Upgrade to Prime (bypasses all restrictions)"
    
    def add_deposit_flag(self, request, queryset):
        """Add deposit flag to selected users"""
        count = queryset.update(has_deposit=True)
        self.message_user(request, f'{count} users marked as having deposits.')
    add_deposit_flag.short_description = "💰 Mark as having deposits"
    
    def reset_to_basic(self, request, queryset):
        """Reset selected users to basic account"""
        count = queryset.update(
            is_verified=False, has_deposit=False, is_basic=True, 
            is_premium=False, is_business=False, is_prime=False
        )
        self.message_user(request, f'{count} users reset to basic accounts.')
    reset_to_basic.short_description = "🔄 Reset to basic accounts"
