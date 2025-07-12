"""
Serializers for Shop Management API
"""

from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Shop, ShopImage, ShopRating, ShopVisit, ShopFollower

class ShopRegistrationSerializer(serializers.ModelSerializer):
    """
    Shop registration serializer for shopkeepers
    """
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = Shop
        fields = [
            'name', 'description', 'category', 'phone_number', 'email',
            'address', 'city', 'ward_number', 'postal_code',
            'pan_number', 'registration_number', 'license_number',
            'opening_time', 'closing_time', 'is_open_24_7', 'closed_days',
            'shop_image', 'latitude', 'longitude'
        ]
    
    def create(self, validated_data):
        """Create shop with location"""
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # Set owner from request user
        validated_data['owner'] = self.context['request'].user
        validated_data['location'] = Point(longitude, latitude)
        
        return Shop.objects.create(**validated_data)


class ShopSerializer(serializers.ModelSerializer):
    """
    Shop serializer for listing and details
    """
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    is_open_now = serializers.ReadOnlyField()
    follower_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'description', 'category', 'phone_number', 'email',
            'address', 'city', 'ward_number', 'opening_time', 'closing_time',
            'is_open_24_7', 'shop_image', 'cover_image', 'is_verified',
            'is_active', 'total_visits', 'total_products', 'average_rating',
            'owner_name', 'latitude', 'longitude', 'distance', 'is_open_now',
            'follower_count', 'is_following', 'created_at'
        ]
    
    def get_latitude(self, obj):
        """Get latitude from location point"""
        if obj.location:
            return obj.location.y
        return None
    
    def get_longitude(self, obj):
        """Get longitude from location point"""
        if obj.location:
            return obj.location.x
        return None
    
    def get_distance(self, obj):
        """Get distance from user location (if provided in context)"""
        user_location = self.context.get('user_location')
        if user_location and obj.location:
            from django.contrib.gis.measure import Distance
            distance = user_location.distance(obj.location)
            return round(distance.km, 2)  # Return distance in kilometers
        return None
    
    def get_follower_count(self, obj):
        """Get number of followers"""
        return obj.followers.count()
    
    def get_is_following(self, obj):
        """Check if current user is following this shop"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(customer=request.user).exists()
        return False


class ShopUpdateSerializer(serializers.ModelSerializer):
    """
    Shop update serializer
    """
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Shop
        fields = [
            'name', 'description', 'category', 'phone_number', 'email',
            'address', 'city', 'ward_number', 'postal_code',
            'opening_time', 'closing_time', 'is_open_24_7', 'closed_days',
            'shop_image', 'cover_image', 'latitude', 'longitude'
        ]
    
    def update(self, instance, validated_data):
        """Update shop with location if provided"""
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        if latitude and longitude:
            instance.location = Point(longitude, latitude)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ShopImageSerializer(serializers.ModelSerializer):
    """
    Shop image serializer
    """
    
    class Meta:
        model = ShopImage
        fields = ['id', 'image', 'caption', 'is_featured', 'created_at']


class ShopRatingSerializer(serializers.ModelSerializer):
    """
    Shop rating and review serializer
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_id = serializers.CharField(source='customer.id', read_only=True)
    
    class Meta:
        model = ShopRating
        fields = [
            'id', 'rating', 'review', 'service_rating', 'product_quality',
            'price_rating', 'is_verified_purchase', 'customer_name',
            'customer_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['customer_name', 'customer_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create rating with customer from request"""
        validated_data['customer'] = self.context['request'].user
        validated_data['shop'] = self.context['shop']
        return super().create(validated_data)


class ShopVisitSerializer(serializers.ModelSerializer):
    """
    Shop visit tracking serializer
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    
    class Meta:
        model = ShopVisit
        fields = [
            'id', 'visit_type', 'visit_duration', 'customer_name',
            'shop_name', 'created_at'
        ]
        read_only_fields = ['customer_name', 'shop_name', 'created_at']


class ShopFollowerSerializer(serializers.ModelSerializer):
    """
    Shop follower serializer
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    
    class Meta:
        model = ShopFollower
        fields = [
            'id', 'notifications_enabled', 'customer_name',
            'shop_name', 'created_at'
        ]
        read_only_fields = ['customer_name', 'shop_name', 'created_at']


class NearbyShopSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for nearby shop search results
    """
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'category', 'address', 'phone_number',
            'shop_image', 'is_verified', 'average_rating', 'is_open_now',
            'latitude', 'longitude', 'distance', 'product_count'
        ]
    
    def get_latitude(self, obj):
        return obj.location.y if obj.location else None
    
    def get_longitude(self, obj):
        return obj.location.x if obj.location else None
    
    def get_distance(self, obj):
        user_location = self.context.get('user_location')
        if user_location and obj.location:
            distance = user_location.distance(obj.location)
            return round(distance.km, 2)
        return None
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()