from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'account_number',
        'ifsc_code', 'ifsc_verified', 'balance', 'is_verified', 'has_deposit',
        'account_level_display', 'is_prime', 'has_set_transfer_pin'
    )

    list_filter = (
        'is_verified', 'has_deposit', 'is_basic', 'is_premium',
        'is_business', 'is_prime', 'has_set_transfer_pin',
        'ifsc_verified', 'is_staff', 'is_active', 'date_joined'
    )

    search_fields = ('username', 'email', 'first_name', 'last_name', 'account_number', 'ifsc_code')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Banking Information', {
            'fields': (
                'phone', 'country', 'residential_address', 'account_number',
                'balance', 'transfer_pin', 'has_set_transfer_pin'
            )
        }),
        ('IFSC Code', {
            'fields': ('ifsc_code', 'ifsc_verified'),
            'description': 'IFSC code for wire transfers. Tick "IFSC verified" to reveal the code to the user.'
        }),
        ('Account Verification & Tiers', {
            'fields': (
                'is_verified', 'has_deposit', 'is_basic', 'is_premium',
                'is_business', 'is_prime'
            ),
            'description': 'Banking verification levels. Prime accounts bypass most restrictions.'
        }),
    )

    readonly_fields = ('account_number', 'ifsc_code', 'has_set_transfer_pin')

    def account_level_display(self, obj):
        return obj.get_account_level()
    account_level_display.short_description = 'Account Level'

    actions = ['verify_ifsc', 'revoke_ifsc', 'make_verified', 'make_prime', 'add_deposit_flag', 'reset_to_basic']

    def verify_ifsc(self, request, queryset):
        from notifications.models import Notification
        updated = 0
        for user in queryset.filter(ifsc_verified=False):
            user.ifsc_verified = True
            user.save(update_fields=['ifsc_verified'])
            Notification.objects.create(
                user=user,
                title='✅ IFSC Code Verified',
                message='Your IFSC code has been verified by the admin. You can now view it on your Dashboard and Settings, and use it for Wire Transfers.',
                notification_type='SECURITY'
            )
            updated += 1
        self.message_user(request, f'{updated} IFSC code(s) marked as verified.')
    verify_ifsc.short_description = '✅ Mark IFSC as verified (reveals code to user)'

    def revoke_ifsc(self, request, queryset):
        count = queryset.filter(ifsc_verified=True).update(ifsc_verified=False)
        self.message_user(request, f'{count} IFSC verification(s) revoked.')
    revoke_ifsc.short_description = '❌ Revoke IFSC verification'

    def make_verified(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f'{count} users marked as verified.')
    make_verified.short_description = '✓ Mark as verified'

    def make_prime(self, request, queryset):
        count = queryset.update(is_prime=True, is_verified=True, has_deposit=True)
        self.message_user(request, f'{count} users upgraded to Prime.')
    make_prime.short_description = '⭐ Upgrade to Prime (bypasses all restrictions)'

    def add_deposit_flag(self, request, queryset):
        count = queryset.update(has_deposit=True)
        self.message_user(request, f'{count} users marked as having deposits.')
    add_deposit_flag.short_description = '💰 Mark as having deposits'

    def reset_to_basic(self, request, queryset):
        count = queryset.update(
            is_verified=False, has_deposit=False, is_basic=True,
            is_premium=False, is_business=False, is_prime=False
        )
        self.message_user(request, f'{count} users reset to basic accounts.')
    reset_to_basic.short_description = '🔄 Reset to basic accounts'
