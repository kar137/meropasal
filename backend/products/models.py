"""
Product Management Models for Pasale App
Handles product catalog, inventory, and pricing
"""

from django.db import models
from shops.models import Shop
import uuid

class ProductCategory(models.Model):
    """
    Product categories for better organization
    """
    name = models.CharField(max_length=50, unique=True)
    name_nepali = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name for frontend")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_categories'
        verbose_name_plural = 'Product Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model for shop inventory
    """
    
    # Units of measurement
    PIECE = 'piece'
    KG = 'kg'
    GRAM = 'gram'
    LITER = 'liter'
    ML = 'ml'
    PACKET = 'packet'
    BOX = 'box'
    BOTTLE = 'bottle'
    
    UNIT_CHOICES = [
        (PIECE, 'Piece'),
        (KG, 'Kilogram'),
        (GRAM, 'Gram'),
        (LITER, 'Liter'),
        (ML, 'Milliliter'),
        (PACKET, 'Packet'),
        (BOX, 'Box'),
        (BOTTLE, 'Bottle'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Product information
    name = models.CharField(max_length=100)
    name_nepali = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=50, blank=True)
    
    # Pricing and inventory
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=PIECE)
    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5, help_text="Alert when stock goes below this")
    
    # Product details
    barcode = models.CharField(max_length=50, blank=True, unique=True, null=True)
    sku = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in grams")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")
    
    # Media
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # SEO and search
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    search_keywords = models.TextField(blank=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['shop', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['is_featured']),
        ]
        unique_together = ['shop', 'name']  # Prevent duplicate product names in same shop
    
    def __str__(self):
        return f"{self.name} - {self.shop.name}"
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        return self.stock_quantity <= self.minimum_stock
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 1)
        return 0
    
    def increment_view_count(self):
        """Increment product view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def update_stock(self, quantity_change, reason=""):
        """Update stock quantity"""
        self.stock_quantity += quantity_change
        if self.stock_quantity < 0:
            self.stock_quantity = 0
        self.save(update_fields=['stock_quantity'])
        
        # Create stock movement record
        ProductStockMovement.objects.create(
            product=self,
            quantity_change=quantity_change,
            new_stock_level=self.stock_quantity,
            reason=reason
        )


class ProductImage(models.Model):
    """
    Additional images for products
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image"


class ProductStockMovement(models.Model):
    """
    Track stock movements for inventory management
    """
    STOCK_IN = 'stock_in'
    STOCK_OUT = 'stock_out'
    ADJUSTMENT = 'adjustment'
    SALE = 'sale'
    RETURN = 'return'
    DAMAGE = 'damage'
    
    MOVEMENT_TYPES = [
        (STOCK_IN, 'Stock In'),
        (STOCK_OUT, 'Stock Out'),
        (ADJUSTMENT, 'Adjustment'),
        (SALE, 'Sale'),
        (RETURN, 'Return'),
        (DAMAGE, 'Damage'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, default=ADJUSTMENT)
    quantity_change = models.IntegerField(help_text="Positive for increase, negative for decrease")
    new_stock_level = models.PositiveIntegerField()
    reason = models.CharField(max_length=200, blank=True)
    reference_id = models.CharField(max_length=100, blank=True, help_text="Order ID, Transaction ID, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'product_stock_movements'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity_change}"


class ProductReview(models.Model):
    """
    Customer reviews for products
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='product_reviews')
    
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    
    # Review aspects
    quality_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    value_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    
    is_verified_purchase = models.BooleanField(default=False)
    is_helpful = models.PositiveIntegerField(default=0, help_text="Number of helpful votes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_reviews'
        unique_together = ['product', 'customer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.customer.full_name}"


class ProductWishlist(models.Model):
    """
    Customer wishlist for products
    """
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_wishlist'
        unique_together = ['customer', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.product.name}"


class ProductPriceHistory(models.Model):
    """
    Track product price changes
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    change_reason = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_price_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.old_price} → {self.new_price}"