from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'account_number',
        'ifsc_code', 'ifsc_verified', 'balance', 'can_transfer_enabled',
        'is_prime', 'has_set_transfer_pin'
    )

    list_filter = (
        'can_transfer_enabled', 'is_prime', 'has_set_transfer_pin',
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
        ('IFSC Verification', {
            'fields': ('ifsc_verified', 'ifsc_code'),
            'description': 'Tick "IFSC verified" to reveal the user\'s IFSC code on the app.'
        }),
        ('Wire Transfer Access', {
            'fields': ('can_transfer_enabled', 'transfer_block_message', 'is_prime'),
            'description': 'Use "can_transfer_enabled" to allow wire transfers. If disabled, the custom block message is shown to the user. Prime bypasses all transfer restrictions.'
        }),
    )

    readonly_fields = ('account_number', 'ifsc_code', 'has_set_transfer_pin')

    actions = [
        'verify_ifsc', 'revoke_ifsc', 'make_prime',
        'enable_transfer_access', 'disable_transfer_access'
    ]

    def verify_ifsc(self, request, queryset):
        from notifications.models import Notification

        updated = 0
        for user in queryset.filter(ifsc_verified=False):
            user.ifsc_verified = True
            user.save(update_fields=['ifsc_verified'])
            Notification.objects.create(
                user=user,
                title='IFSC Code Verified',
                message='Your IFSC code has been verified by the admin. You can now view it on your Dashboard and Settings, and use it for Wire Transfers.',
                notification_type='SECURITY'
            )
            updated += 1
        self.message_user(request, f'{updated} IFSC code(s) marked as verified.')

    verify_ifsc.short_description = 'Mark IFSC as verified (reveals code to user)'

    def revoke_ifsc(self, request, queryset):
        count = queryset.filter(ifsc_verified=True).update(ifsc_verified=False)
        self.message_user(request, f'{count} IFSC verification(s) revoked.')

    revoke_ifsc.short_description = 'Revoke IFSC verification'

    def make_prime(self, request, queryset):
        count = queryset.update(is_prime=True, can_transfer_enabled=True)
        self.message_user(request, f'{count} users upgraded to Prime.')

    make_prime.short_description = 'Upgrade to Prime (bypasses all restrictions)'

    def enable_transfer_access(self, request, queryset):
        count = queryset.update(can_transfer_enabled=True, transfer_block_message='')
        self.message_user(request, f'{count} users can now make wire transfers.')

    enable_transfer_access.short_description = 'Enable wire transfer access'

    def disable_transfer_access(self, request, queryset):
        count = queryset.update(can_transfer_enabled=False)
        self.message_user(request, f'{count} users blocked from wire transfers.')

    disable_transfer_access.short_description = 'Disable wire transfer access'
