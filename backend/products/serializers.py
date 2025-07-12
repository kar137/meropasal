"""
Serializers for Product Management API
"""

from rest_framework import serializers
from .models import (
    ProductCategory, Product, ProductImage, ProductStockMovement,
    ProductReview, ProductWishlist, ProductPriceHistory
)

class ProductCategorySerializer(serializers.ModelSerializer):
    """
    Product category serializer
    """
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'name_nepali', 'description', 'icon', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Product image serializer
    """
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """
    Product serializer for listing and details
    """
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    shop_id = serializers.CharField(source='shop.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_wishlisted = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_nepali', 'description', 'brand',
            'price', 'original_price', 'unit', 'stock_quantity',
            'barcode', 'sku', 'weight', 'dimensions', 'image',
            'is_active', 'is_featured', 'is_available', 'tags',
            'view_count', 'order_count', 'shop_name', 'shop_id',
            'category_name', 'images', 'is_in_stock', 'is_low_stock',
            'discount_percentage', 'is_wishlisted', 'average_rating',
            'review_count', 'created_at', 'updated_at'
        ]
    
    def get_is_wishlisted(self, obj):
        """Check if product is in user's wishlist"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlisted_by.filter(customer=request.user).exists()
        return False
    
    def get_average_rating(self, obj):
        """Get average rating for product"""
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0.0
    
    def get_review_count(self, obj):
        """Get number of reviews"""
        return obj.reviews.count()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Product serializer for creation and updates
    """
    
    class Meta:
        model = Product
        fields = [
            'name', 'name_nepali', 'description', 'brand', 'category',
            'price', 'original_price', 'unit', 'stock_quantity',
            'minimum_stock', 'barcode', 'sku', 'weight', 'dimensions',
            'image', 'is_featured', 'is_available', 'tags', 'search_keywords'
        ]
    
    def create(self, validated_data):
        """Create product with shop from request"""
        validated_data['shop'] = self.context['request'].user.shop
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update product and track price changes"""
        old_price = instance.price
        new_price = validated_data.get('price', old_price)
        
        # Track price change
        if old_price != new_price:
            ProductPriceHistory.objects.create(
                product=instance,
                old_price=old_price,
                new_price=new_price,
                change_reason="Price updated by shopkeeper"
            )
        
        return super().update(instance, validated_data)


class ProductStockMovementSerializer(serializers.ModelSerializer):
    """
    Product stock movement serializer
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductStockMovement
        fields = [
            'id', 'movement_type', 'quantity_change', 'new_stock_level',
            'reason', 'reference_id', 'product_name', 'created_at'
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Product review serializer
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_id = serializers.CharField(source='customer.id', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'rating', 'review', 'quality_rating', 'value_rating',
            'is_verified_purchase', 'is_helpful', 'customer_name',
            'customer_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['customer_name', 'customer_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create review with customer and product from context"""
        validated_data['customer'] = self.context['request'].user
        validated_data['product'] = self.context['product']
        return super().create(validated_data)


class ProductWishlistSerializer(serializers.ModelSerializer):
    """
    Product wishlist serializer
    """
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = ProductWishlist
        fields = ['id', 'product', 'created_at']


class ProductSearchSerializer(serializers.ModelSerializer):
    """
    Simplified product serializer for search results
    """
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    shop_distance = serializers.SerializerMethodField()
    shop_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'original_price', 'unit',
            'image', 'is_available', 'stock_quantity',
            'shop_name', 'shop_distance', 'shop_location',
            'discount_percentage'
        ]
    
    def get_shop_distance(self, obj):
        """Get distance to shop from user location"""
        user_location = self.context.get('user_location')
        if user_location and obj.shop.location:
            distance = user_location.distance(obj.shop.location)
            return round(distance.km, 2)
        return None
    
    def get_shop_location(self, obj):
        """Get shop location coordinates"""
        if obj.shop.location:
            return {
                'latitude': obj.shop.location.y,
                'longitude': obj.shop.location.x
            }
        return None


class ProductStockUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating product stock
    """
    quantity_change = serializers.IntegerField()
    movement_type = serializers.ChoiceField(choices=ProductStockMovement.MOVEMENT_TYPES)
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)
    reference_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        """Update product stock"""
        quantity_change = validated_data['quantity_change']
        movement_type = validated_data['movement_type']
        reason = validated_data.get('reason', '')
        reference_id = validated_data.get('reference_id', '')
        
        # Update stock
        old_stock = instance.stock_quantity
        instance.stock_quantity += quantity_change
        if instance.stock_quantity < 0:
            instance.stock_quantity = 0
        instance.save(update_fields=['stock_quantity'])
        
        # Create stock movement record
        ProductStockMovement.objects.create(
            product=instance,
            movement_type=movement_type,
            quantity_change=quantity_change,
            new_stock_level=instance.stock_quantity,
            reason=reason,
            reference_id=reference_id
        )
        
        return instance