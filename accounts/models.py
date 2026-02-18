from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random

class User(AbstractUser):
    """Custom user model for banking application"""
    
    # Override email to make it unique and required
    email = models.EmailField(unique=True)
    
    # Basic user information
    phone = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    residential_address = models.TextField(blank=True, null=True)
    
    # Banking-specific fields
    account_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    transfer_pin = models.CharField(max_length=255, blank=True, null=True, help_text="Encrypted transfer PIN")
    
    # Account verification flags
    is_verified = models.BooleanField(default=False, help_text="Basic email/phone verification")
    has_deposit = models.BooleanField(default=False, help_text="User has made initial deposit")
    has_set_transfer_pin = models.BooleanField(default=False)
    
    # Account level tiers
    is_basic = models.BooleanField(default=True, help_text="Basic account tier")
    is_premium = models.BooleanField(default=False, help_text="Premium tier with higher limits")
    is_business = models.BooleanField(default=False, help_text="Business account features")
    is_prime = models.BooleanField(default=False, help_text="Tier 0 - Bypasses all checks")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate 10-digit account number if not exists
        if not self.account_number:
            while True:
                account_num = str(random.randint(1000000000, 9999999999))
                if not User.objects.filter(account_number=account_num).exists():
                    self.account_number = account_num
                    break
        
        # Set default transfer PIN of 1234 for new users
        is_new_user = self.pk is None
        
        super().save(*args, **kwargs)
        
        if is_new_user and not self.transfer_pin:
            self.transfer_pin = '1234'
            self.has_set_transfer_pin = True
    
    def set_transfer_pin(self, pin):
        """Set the transfer PIN in plain text"""
        if len(str(pin)) != 4 or not str(pin).isdigit():
            raise ValueError("Transfer PIN must be exactly 4 digits")
        self.transfer_pin = str(pin)
        self.has_set_transfer_pin = True
        self.save()
    
    def check_transfer_pin(self, pin):
        """Check if provided PIN matches the stored transfer PIN"""
        if not self.transfer_pin:
            return False
        return str(pin) == self.transfer_pin
    
    def can_transfer(self):
        """Check if user is eligible to make transfers according to banking rules"""
        from decimal import Decimal
        
        # Prime accounts bypass all checks
        if self.is_prime:
            return True, "Prime account - all checks bypassed"
        
        # Check basic requirements
        if not self.is_verified:
            return False, "Account not verified. Please verify your email and phone."
        
        if not self.has_deposit:
            return False, "Please make an initial deposit to activate transfers."
        
        if not self.has_set_transfer_pin:
            return False, "Please set up your transfer PIN in Settings."
        
        # Check account tier balance limits - transaction FAILS if balance exceeds limits
        if self.is_basic and self.balance > Decimal('5000.00'):
            return False, "Your account is locked temporarily. Contact customer assistance for help."
        
        if self.is_premium and self.balance > Decimal('19000.00'):
            return False, "Your account is locked temporarily. Contact customer assistance for help."
        
        # Business accounts have no balance limits - transactions proceed normally
        # Prime accounts bypass all these checks entirely
        
        # All checks passed
        return True, "Transfer authorized"
    
    def get_account_level(self):
        """Get the user's account level for display purposes"""
        if self.is_prime:
            return "Prime"
        elif self.is_business:
            return "Business"
        elif self.is_premium:
            return "Premium"
        elif self.is_basic:
            return "Basic"
        else:
            return "Unverified"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.account_number})"
