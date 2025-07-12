"""
Shop Management Models for Pasale App
Handles shop registration, verification, and management
"""

from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from accounts.models import User
import uuid

class Shop(models.Model):
    """
    Shop model for shopkeepers
    Contains shop information, location, and verification status
    """
    
    # Shop categories
    GROCERY = 'grocery'
    ELECTRONICS = 'electronics'
    FASHION = 'fashion'
    PHARMACY = 'pharmacy'
    RESTAURANT = 'restaurant'
    HARDWARE = 'hardware'
    STATIONERY = 'stationery'
    OTHER = 'other'
    
    CATEGORY_CHOICES = [
        (GROCERY, 'Grocery Store'),
        (ELECTRONICS, 'Electronics'),
        (FASHION, 'Fashion & Clothing'),
        (PHARMACY, 'Pharmacy'),
        (RESTAURANT, 'Restaurant/Food'),
        (HARDWARE, 'Hardware Store'),
        (STATIONERY, 'Stationery'),
        (OTHER, 'Other'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    
    # Shop information
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=OTHER)
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?977[0-9]{10}$',
        message="Phone number must be in format: '+977XXXXXXXXXX'"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    email = models.EmailField(blank=True)
    
    # Location information
    location = models.PointField(help_text="Shop's exact coordinates")
    address = models.TextField()
    city = models.CharField(max_length=50, default='Kathmandu')
    ward_number = models.PositiveIntegerField(help_text="Ward number")
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Business information
    pan_number = models.CharField(max_length=20, blank=True, help_text="PAN/VAT Number")
    registration_number = models.CharField(max_length=50, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    
    # Operating hours
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_open_24_7 = models.BooleanField(default=False)
    closed_days = models.CharField(
        max_length=20,
        blank=True,
        help_text="Comma-separated days (e.g., 'saturday,sunday')"
    )
    
    # Media
    shop_image = models.ImageField(upload_to='shops/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='shops/covers/', null=True, blank=True)
    
    # Verification and status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Statistics
    total_visits = models.PositiveIntegerField(default=0)
    total_products = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shops'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_active']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    @property
    def is_open_now(self):
        """Check if shop is currently open"""
        from datetime import datetime, time
        
        if self.is_open_24_7:
            return True
        
        now = datetime.now().time()
        return self.opening_time <= now <= self.closing_time
    
    def increment_visit_count(self):
        """Increment shop visit count"""
        self.total_visits += 1
        self.save(update_fields=['total_visits'])


class ShopImage(models.Model):
    """
    Additional images for shops
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='shops/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shop_images'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.shop.name} - Image"


class ShopRating(models.Model):
    """
    Customer ratings and reviews for shops
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_ratings')
    
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    
    # Specific rating categories
    service_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    product_quality = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    price_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shop_ratings'
        unique_together = ['shop', 'customer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.shop.name} - {self.rating}★ by {self.customer.full_name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update shop's average rating
        self.shop.update_average_rating()


class ShopVisit(models.Model):
    """
    Track customer visits to shops for analytics
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='visits')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_visits')
    
    visit_location = models.PointField(help_text="Customer's location during visit")
    visit_duration = models.DurationField(null=True, blank=True)
    
    # Visit context
    visit_type = models.CharField(
        max_length=20,
        choices=[
            ('browse', 'Browsing'),
            ('purchase', 'Purchase'),
            ('inquiry', 'Inquiry'),
            ('qr_scan', 'QR Scan'),
        ],
        default='browse'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shop_visits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.full_name} visited {self.shop.name}"


class ShopFollower(models.Model):
    """
    Customer following shops for updates
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='followers')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_shops')
    
    notifications_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shop_followers'
        unique_together = ['shop', 'customer']
    
    def __str__(self):
        return f"{self.customer.full_name} follows {self.shop.name}"


# Add method to Shop model to update average rating
def update_average_rating(self):
    """Update shop's average rating"""
    from django.db.models import Avg
    
    avg_rating = self.ratings.aggregate(Avg('rating'))['rating__avg']
    self.average_rating = avg_rating or 0.00
    self.save(update_fields=['average_rating'])

# Add the method to Shop model
Shop.update_average_rating = update_average_rating