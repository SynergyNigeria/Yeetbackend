from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from accounts.models import User
from .models import Transaction
from notifications.models import Notification


class TransferService:
    """Service class for handling all transfer operations with banking rules"""
    
    @staticmethod
    def validate_transfer_request(sender, recipient_account, amount, transfer_pin, message=""):
        """Validate a transfer request according to banking rules"""
        
        # Basic validations
        if amount <= 0:
            return False, "Transfer amount must be positive"
        
        if not recipient_account:
            return False, "Recipient account number is required"
        
        # Check if recipient exists
        try:
            recipient = User.objects.get(account_number=recipient_account)
        except User.DoesNotExist:
            return False, "Recipient account not found"
        
        # Check for self-transfer
        if sender == recipient:
            return False, "Cannot transfer to your own account"
        
        # Check sender's transfer eligibility
        can_transfer, transfer_message = sender.can_transfer()
        if not can_transfer:
            return False, transfer_message
        
        # Validate transfer PIN (unless prime account)
        if not sender.is_prime:
            if not transfer_pin:
                return False, "Transfer PIN is required"
            
            if not sender.check_transfer_pin(transfer_pin):
                return False, "Invalid transfer PIN"
        
        # Check sufficient balance
        if sender.balance < amount:
            return False, f"Insufficient balance. Available: ${sender.balance}"
        
        return True, {
            'recipient': recipient,
            'message': 'Transfer validation successful'
        }
    
    @staticmethod
    def process_internal_transfer(sender, recipient_account, amount, transfer_pin, message=""):
        """Process an internal transfer between YEET Bank users"""
        
        # Validate the transfer
        is_valid, validation_result = TransferService.validate_transfer_request(
            sender, recipient_account, amount, transfer_pin, message
        )
        
        if not is_valid:
            return False, None, validation_result  # validation_result is error message
        
        recipient = validation_result['recipient']
        
        # Process the transfer in a database transaction
        try:
            with db_transaction.atomic():
                # Create the transaction record
                transfer_transaction = Transaction.objects.create(
                    transaction_type='TRANSFER',
                    amount=Decimal(str(amount)),
                    description=message or f"Transfer to {recipient.get_full_name()}",
                    sender=sender,
                    recipient=recipient,
                    recipient_account=recipient_account,
                    status='COMPLETED',
                    completed_at=timezone.now()
                )
                
                # Update balances
                sender.balance -= Decimal(str(amount))
                recipient.balance += Decimal(str(amount))
                
                # Save users
                sender.save()
                recipient.save()
                
                # Create notifications
                TransferService._create_transfer_notifications(
                    transfer_transaction, sender, recipient, amount
                )
                
                return True, transfer_transaction, "Transfer completed successfully"
                
        except Exception as e:
            # If anything goes wrong, return error
            return False, None, f"Transfer failed: {str(e)}"
    
    @staticmethod
    def process_external_transfer(sender, recipient_account, amount, transfer_pin, message=""):
        """Process an external transfer (simulated)"""
        
        # For external transfers, we don't validate recipient existence
        # but we still use common validation rules
        
        # Basic validations
        if amount <= 0:
            return False, None, "Transfer amount must be positive"
        
        if not recipient_account:
            return False, None, "Recipient account number is required"
        
        # Check sender's transfer eligibility (includes balance limits)
        can_transfer, transfer_message = sender.can_transfer()
        if not can_transfer:
            return False, None, transfer_message
        
        # Validate transfer PIN (unless prime account)
        if not sender.is_prime:
            if not transfer_pin:
                return False, None, "Transfer PIN is required"
            
            if not sender.check_transfer_pin(transfer_pin):
                return False, None, "Invalid transfer PIN"
        
        # Check sufficient balance (add small fee for external transfers)
        external_fee = Decimal('1.00')  # $1 fee for external transfers
        total_amount = Decimal(str(amount)) + external_fee
        
        if sender.balance < total_amount:
            return False, None, f"Insufficient balance. Required: ${total_amount} (including ${external_fee} fee)"
        
        # Process the external transfer
        try:
            with db_transaction.atomic():
                # Create the transaction record
                transfer_transaction = Transaction.objects.create(
                    transaction_type='TRANSFER',
                    amount=Decimal(str(amount)),
                    description=message or f"External transfer to {recipient_account}",
                    sender=sender,
                    recipient=None,  # No recipient for external transfers
                    recipient_account=recipient_account,
                    status='COMPLETED',
                    completed_at=timezone.now()
                )
                
                # Deduct amount + fee from sender
                sender.balance -= total_amount
                sender.save()
                
                # Create notification for sender
                Notification.objects.create(
                    user=sender,
                    title='💸 External Transfer Sent',
                    message=f'External transfer of ${amount} to {recipient_account} completed successfully. Fee: ${external_fee}',
                    notification_type='TRANSACTION',
                    transaction=transfer_transaction
                )
                
                return True, transfer_transaction, f"External transfer completed successfully. Fee: ${external_fee}"
                
        except Exception as e:
            return False, None, f"External transfer failed: {str(e)}"
    
    @staticmethod
    def _create_transfer_notifications(transaction_obj, sender, recipient, amount):
        """Create in-app notifications and send emails for both sender and recipient"""
        
        # Notification for sender
        Notification.objects.create(
            user=sender,
            title='💸 Transfer Sent',
            message=f'You sent ${amount} to {recipient.get_full_name()} ({recipient.account_number})',
            notification_type='TRANSACTION',
            transaction=transaction_obj
        )
        
        # Notification for recipient
        Notification.objects.create(
            user=recipient,
            title='💰 Money Received',
            message=f'You received ${amount} from {sender.get_full_name()} ({sender.account_number})',
            notification_type='TRANSACTION',
            transaction=transaction_obj
        )

        # Send money-received email to recipient
        try:
            from accounts.email_utils import send_money_received_email
            send_money_received_email(
                recipient=recipient,
                sender=sender,
                amount=amount,
                transaction=transaction_obj,
            )
        except Exception:
            pass  # Email failure must never break the transfer