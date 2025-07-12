"""
User Authentication Models for Pasale App
Supports both Customer (ग्राहक) and Shopkeeper (पसलधारक) roles
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
import uuid

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Supports role-based authentication for customers and shopkeepers
    """
    
    # User roles
    CUSTOMER = 'customer'
    SHOPKEEPER = 'shopkeeper'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'ग्राहक (Customer)'),
        (SHOPKEEPER, 'पसलधारक (Shopkeeper)'),
        (ADMIN, 'Admin'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?977[0-9]{10}$',
        message="Phone number must be in format: '+977XXXXXXXXXX' or '977XXXXXXXXXX'"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    
    # Profile information
    full_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Location (for customers - last known location)
    location = models.PointField(null=True, blank=True, help_text="User's location coordinates")
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, default='Kathmandu')
    
    # Preferences
    language_preference = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('ne', 'नेपाली')],
        default='ne'
    )
    notifications_enabled = models.BooleanField(default=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    @property
    def is_customer(self):
        return self.role == self.CUSTOMER
    
    @property
    def is_shopkeeper(self):
        return self.role == self.SHOPKEEPER
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN


class UserWallet(models.Model):
    """
    Digital wallet for reward tokens
    Both customers and shopkeepers have wallets
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.PositiveIntegerField(default=0, help_text="Token balance")
    total_earned = models.PositiveIntegerField(default=0, help_text="Total tokens earned")
    total_spent = models.PositiveIntegerField(default=0, help_text="Total tokens spent")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_wallets'
    
    def __str__(self):
        return f"{self.user.full_name}'s Wallet - {self.balance} tokens"
    
    def add_tokens(self, amount, reason=""):
        """Add tokens to wallet"""
        self.balance += amount
        self.total_earned += amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='credit',
            amount=amount,
            reason=reason
        )
    
    def deduct_tokens(self, amount, reason=""):
        """Deduct tokens from wallet"""
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            self.save()
            
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='debit',
                amount=amount,
                reason=reason
            )
            return True
        return False


class WalletTransaction(models.Model):
    """
    Track all wallet transactions for transparency
    """
    CREDIT = 'credit'
    DEBIT = 'debit'
    
    TRANSACTION_TYPES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]
    
    wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.PositiveIntegerField()
    reason = models.CharField(max_length=200)
    balance_after = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Store balance after transaction
        self.balance_after = self.wallet.balance
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.wallet.user.full_name} - {self.transaction_type} {self.amount}"


class UserSession(models.Model):
    """
    Track user sessions for analytics and security
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_id = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)  # android, ios
    app_version = models.CharField(max_length=20)
    location = models.PointField(null=True, blank=True)
    
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.device_type} - {self.login_time}"