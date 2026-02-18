from rest_framework import serializers
from decimal import Decimal
from .models import Transaction, TransactionReport
from accounts.models import User

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'transaction_type', 'amount', 'description',
            'status', 'sender', 'sender_name', 'recipient', 'recipient_name',
            'recipient_account', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'created_at', 'completed_at']


class YeetTransferSerializer(serializers.Serializer):
    """Serializer for YEET transfer requests"""
    
    recipient_account = serializers.CharField(max_length=20, required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    transfer_pin = serializers.CharField(max_length=6, required=False, allow_blank=True)
    message = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > Decimal('999999.99'):
            raise serializers.ValidationError("Amount exceeds maximum limit")
        return value
    
    def validate_recipient_account(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Recipient account number is required")
        return value.strip()
    
    def validate(self, attrs):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User context is required")
        
        # Check if user is trying to transfer to themselves
        recipient_account = attrs.get('recipient_account', '').strip()
        if recipient_account == user.account_number:
            raise serializers.ValidationError("Cannot transfer to your own account")
        
        return attrs

class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transactions"""
    
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description', 'recipient_account']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        transaction_type = attrs.get('transaction_type')
        
        if transaction_type in ['TRANSFER', 'PAYMENT']:
            if not attrs.get('recipient_account'):
                raise serializers.ValidationError("Recipient account is required for transfers and payments")
            
            # Check if recipient exists (fixed the bug here)
            try:
                recipient = User.objects.get(account_number=attrs['recipient_account'])
                attrs['recipient'] = recipient
            except User.DoesNotExist:
                raise serializers.ValidationError("Recipient account not found")
        
        # Check balance for withdrawals and transfers
        if transaction_type in ['WITHDRAWAL', 'TRANSFER', 'PAYMENT']:
            if user.balance < attrs['amount']:
                raise serializers.ValidationError("Insufficient balance")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class TransactionReportSerializer(serializers.ModelSerializer):
    """Serializer for TransactionReport model"""
    
    transaction_details = TransactionSerializer(source='transaction', read_only=True)
    reporter_name = serializers.CharField(source='reporter.get_full_name', read_only=True)
    
    class Meta:
        model = TransactionReport
        fields = [
            'id', 'transaction', 'transaction_details', 'reporter', 'reporter_name',
            'reason', 'description', 'status', 'admin_notes', 'resolution',
            'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = [
            'id', 'reporter', 'reporter_name', 'status', 'admin_notes',
            'resolution', 'created_at', 'updated_at', 'resolved_at'
        ]


class CreateTransactionReportSerializer(serializers.ModelSerializer):
    """Serializer for creating transaction reports"""
    
    class Meta:
        model = TransactionReport
        fields = ['transaction', 'reason', 'description']
    
    def validate_transaction(self, value):
        """Ensure user can only report their own transactions"""
        user = self.context['request'].user
        if value.sender != user and (value.recipient and value.recipient != user):
            raise serializers.ValidationError("You can only report your own transactions")
        return value