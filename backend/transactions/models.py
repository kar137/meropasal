"""
Transaction and QR Code Models for Pasale App
Handles QR verification, rewards, and transaction tracking
"""

from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from shops.models import Shop
from products.models import Product
import uuid
import hashlib
import qrcode
from io import BytesIO
from django.core.files import File
import json
from datetime import datetime, timedelta

class QRTransaction(models.Model):
    """
    QR Code transactions for shop visits and rewards
    """
    
    # Transaction types
    VISIT = 'visit'
    PURCHASE = 'purchase'
    REFERRAL = 'referral'
    SPECIAL = 'special'
    
    TRANSACTION_TYPES = [
        (VISIT, 'Shop Visit'),
        (PURCHASE, 'Purchase'),
        (REFERRAL, 'Referral'),
        (SPECIAL, 'Special Offer'),
    ]
    
    # Transaction status
    PENDING = 'pending'
    VERIFIED = 'verified'
    EXPIRED = 'expired'
    INVALID = 'invalid'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (VERIFIED, 'Verified'),
        (EXPIRED, 'Expired'),
        (INVALID, 'Invalid'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=50, unique=True)
    
    # Participants
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='qr_transactions')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qr_transactions', null=True, blank=True)
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default=VISIT)
    reward_amount = models.PositiveIntegerField(default=0, help_text="Reward tokens")
    
    # QR Code data
    qr_data = models.JSONField(help_text="QR code payload")
    qr_hash = models.CharField(max_length=64, help_text="SHA256 hash for verification")
    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    
    # Location verification
    generated_location = models.PointField(help_text="Location where QR was generated")
    scanned_location = models.PointField(null=True, blank=True, help_text="Location where QR was scanned")
    max_distance_meters = models.PositiveIntegerField(default=500, help_text="Maximum allowed distance for verification")
    
    # Timing
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    scanned_at = models.DateTimeField(null=True, blank=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    verification_notes = models.TextField(blank=True)
    
    # Additional data
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_items = models.JSONField(null=True, blank=True, help_text="List of purchased products")
    
    class Meta:
        db_table = 'qr_transactions'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['shop', 'status']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"QR-{self.transaction_id} - {self.shop.name}"
    
    def save(self, *args, **kwargs):
        # Generate transaction ID if not exists
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Set expiry time if not set
        if not self.expires_at:
            from django.conf import settings
            expiry_minutes = getattr(settings, 'QR_CODE_EXPIRY_MINUTES', 30)
            self.expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        
        # Generate QR hash
        if not self.qr_hash:
            self.qr_hash = self.generate_qr_hash()
        
        super().save(*args, **kwargs)
        
        # Generate QR code image after saving
        if not self.qr_image:
            self.generate_qr_image()
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        shop_code = self.shop.id.hex[:6].upper()
        return f"{timestamp}{shop_code}"
    
    def generate_qr_hash(self):
        """Generate verification hash for QR code"""
        data = {
            'transaction_id': self.transaction_id,
            'shop_id': str(self.shop.id),
            'transaction_type': self.transaction_type,
            'reward_amount': self.reward_amount,
            'generated_at': self.generated_at.isoformat() if self.generated_at else datetime.now().isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        
        # Store QR data
        self.qr_data = data
        
        # Generate hash
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def generate_qr_image(self):
        """Generate QR code image"""
        try:
            # QR code content
            qr_content = {
                'transaction_id': self.transaction_id,
                'shop_id': str(self.shop.id),
                'hash': self.qr_hash,
                'expires_at': self.expires_at.isoformat()
            }
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_content))
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to file
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            filename = f"qr_{self.transaction_id}.png"
            self.qr_image.save(filename, File(buffer), save=False)
            
            # Save without triggering save() again
            super().save(update_fields=['qr_image'])
            
        except Exception as e:
            print(f"Error generating QR image: {e}")
    
    def verify_scan(self, customer, scan_location, scanned_hash):
        """Verify QR code scan"""
        from django.contrib.gis.measure import Distance
        
        # Check if already scanned
        if self.status != self.PENDING:
            return False, f"QR code already {self.status}"
        
        # Check expiry
        if datetime.now() > self.expires_at.replace(tzinfo=None):
            self.status = self.EXPIRED
            self.save(update_fields=['status'])
            return False, "QR code has expired"
        
        # Verify hash
        if scanned_hash != self.qr_hash:
            self.status = self.INVALID
            self.verification_notes = "Hash verification failed"
            self.save(update_fields=['status', 'verification_notes'])
            return False, "Invalid QR code"
        
        # Verify location (if both locations available)
        if self.generated_location and scan_location:
            distance = self.generated_location.distance(scan_location)
            distance_meters = distance.m
            
            if distance_meters > self.max_distance_meters:
                self.status = self.INVALID
                self.verification_notes = f"Location verification failed. Distance: {distance_meters:.0f}m"
                self.save(update_fields=['status', 'verification_notes'])
                return False, f"You must be within {self.max_distance_meters}m of the shop to scan this QR code"
        
        # Verify successful
        self.customer = customer
        self.scanned_location = scan_location
        self.scanned_at = datetime.now()
        self.status = self.VERIFIED
        self.verification_notes = "Successfully verified"
        self.save(update_fields=['customer', 'scanned_location', 'scanned_at', 'status', 'verification_notes'])
        
        # Award rewards
        self.award_rewards()
        
        return True, "QR code verified successfully"
    
    def award_rewards(self):
        """Award rewards to customer and shopkeeper"""
        if self.status != self.VERIFIED or not self.customer:
            return
        
        try:
            # Award to customer
            customer_wallet = self.customer.wallet
            customer_wallet.add_tokens(
                self.reward_amount,
                f"QR scan reward - {self.shop.name}"
            )
            
            # Award to shopkeeper (50% of customer reward)
            shopkeeper_reward = max(1, self.reward_amount // 2)
            shopkeeper_wallet = self.shop.owner.wallet
            shopkeeper_wallet.add_tokens(
                shopkeeper_reward,
                f"Customer visit reward - {self.customer.full_name}"
            )
            
            # Create reward records
            RewardTransaction.objects.create(
                user=self.customer,
                transaction_type='qr_scan',
                amount=self.reward_amount,
                source_transaction=self,
                description=f"QR scan at {self.shop.name}"
            )
            
            RewardTransaction.objects.create(
                user=self.shop.owner,
                transaction_type='customer_visit',
                amount=shopkeeper_reward,
                source_transaction=self,
                description=f"Customer visit from {self.customer.full_name}"
            )
            
        except Exception as e:
            print(f"Error awarding rewards: {e}")


class RewardTransaction(models.Model):
    """
    Track all reward transactions for transparency
    """
    
    # Reward types
    QR_SCAN = 'qr_scan'
    PURCHASE = 'purchase'
    REFERRAL = 'referral'
    CUSTOMER_VISIT = 'customer_visit'
    BONUS = 'bonus'
    PENALTY = 'penalty'
    
    TRANSACTION_TYPES = [
        (QR_SCAN, 'QR Code Scan'),
        (PURCHASE, 'Purchase'),
        (REFERRAL, 'Referral'),
        (CUSTOMER_VISIT, 'Customer Visit'),
        (BONUS, 'Bonus'),
        (PENALTY, 'Penalty'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(help_text="Positive for credit, negative for debit")
    description = models.CharField(max_length=200)
    
    # References
    source_transaction = models.ForeignKey(QRTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reward_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.transaction_type} - {self.amount}"


class CustomerVisit(models.Model):
    """
    Track customer visits to shops (separate from QR transactions)
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='customer_visits')
    
    # Visit details
    visit_location = models.PointField(help_text="Customer location during visit")
    visit_duration = models.DurationField(null=True, blank=True)
    
    # Visit context
    visit_source = models.CharField(
        max_length=20,
        choices=[
            ('search', 'Product Search'),
            ('browse', 'Browse'),
            ('qr_scan', 'QR Code Scan'),
            ('referral', 'Referral'),
            ('direct', 'Direct'),
        ],
        default='direct'
    )
    
    # Interaction data
    products_viewed = models.JSONField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customer_visits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.full_name} visited {self.shop.name}"


class ReferralCode(models.Model):
    """
    Referral codes for user acquisition
    """
    code = models.CharField(max_length=20, unique=True)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_codes')
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    max_usage = models.PositiveIntegerField(default=100)
    
    # Rewards
    referrer_reward = models.PositiveIntegerField(default=100)
    referee_reward = models.PositiveIntegerField(default=50)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_codes'
    
    def __str__(self):
        return f"{self.code} - {self.referrer.full_name}"
    
    def can_be_used(self):
        """Check if referral code can be used"""
        if not self.is_active:
            return False
        
        if self.usage_count >= self.max_usage:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at.replace(tzinfo=None):
            return False
        
        return True
    
    def use_code(self, referee):
        """Use referral code and award rewards"""
        if not self.can_be_used():
            return False, "Referral code cannot be used"
        
        if referee == self.referrer:
            return False, "Cannot use your own referral code"
        
        try:
            # Award rewards
            referrer_wallet = self.referrer.wallet
            referrer_wallet.add_tokens(
                self.referrer_reward,
                f"Referral reward - {referee.full_name} joined"
            )
            
            referee_wallet = referee.wallet
            referee_wallet.add_tokens(
                self.referee_reward,
                f"Welcome bonus - Used {self.referrer.full_name}'s referral"
            )
            
            # Create reward records
            RewardTransaction.objects.create(
                user=self.referrer,
                transaction_type='referral',
                amount=self.referrer_reward,
                description=f"Referral reward - {referee.full_name}",
                reference_id=self.code
            )
            
            RewardTransaction.objects.create(
                user=referee,
                transaction_type='referral',
                amount=self.referee_reward,
                description=f"Welcome bonus - {self.code}",
                reference_id=self.code
            )
            
            # Update usage count
            self.usage_count += 1
            self.save(update_fields=['usage_count'])
            
            return True, "Referral code used successfully"
            
        except Exception as e:
            return False, f"Error using referral code: {str(e)}"