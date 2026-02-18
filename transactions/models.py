from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

class Transaction(models.Model):
    """Model for banking transactions"""
    
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
        ('PAYMENT', 'Payment'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Transaction details
    transaction_id = models.CharField(max_length=50, unique=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Parties involved
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transactions', blank=True, null=True)
    
    # For transfers/payments
    recipient_account = models.CharField(max_length=20, blank=True, null=True)  # Account number for external transfers
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{str(uuid.uuid4().hex[:12]).upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_id} - {self.amount}"
    
    class Meta:
        ordering = ['-created_at']


class TransactionReport(models.Model):
    """Model for user transaction reports"""
    
    REPORT_REASONS = [
        ('UNAUTHORIZED', 'Unauthorized transaction'),
        ('INCORRECT_AMOUNT', 'Incorrect amount'),
        ('DUPLICATE', 'Duplicate transaction'),
        ('NOT_RECEIVED', 'Payment not received'),
        ('OTHER', 'Other issue'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('INVESTIGATING', 'Under Investigation'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    # Report details
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transaction_reports')
    
    # Report content
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField()
    
    # Status and resolution
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True)
    resolution = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Report {self.id} - {self.transaction.transaction_id} - {self.reason}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['transaction', 'reporter']  # One report per transaction per user
