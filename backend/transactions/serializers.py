"""
Serializers for Transaction and QR Code APIs
"""

from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import QRTransaction, RewardTransaction, CustomerVisit, ReferralCode

class QRTransactionCreateSerializer(serializers.ModelSerializer):
    """
    QR Transaction creation serializer
    """
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = QRTransaction
        fields = [
            'transaction_type', 'reward_amount', 'purchase_amount',
            'product_items', 'max_distance_meters', 'latitude', 'longitude'
        ]
    
    def create(self, validated_data):
        """Create QR transaction with location"""
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        validated_data['shop'] = self.context['request'].user.shop
        validated_data['generated_location'] = Point(longitude, latitude)
        
        return QRTransaction.objects.create(**validated_data)


class QRTransactionSerializer(serializers.ModelSerializer):
    """
    QR Transaction serializer for listing and details
    """
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    qr_image_url = serializers.SerializerMethodField()
    generated_latitude = serializers.SerializerMethodField()
    generated_longitude = serializers.SerializerMethodField()
    scanned_latitude = serializers.SerializerMethodField()
    scanned_longitude = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = QRTransaction
        fields = [
            'id', 'transaction_id', 'transaction_type', 'reward_amount',
            'status', 'shop_name', 'customer_name', 'qr_image_url',
            'generated_latitude', 'generated_longitude', 'scanned_latitude',
            'scanned_longitude', 'generated_at', 'expires_at', 'scanned_at',
            'time_remaining', 'verification_notes', 'purchase_amount'
        ]
    
    def get_qr_image_url(self, obj):
        """Get QR code image URL"""
        if obj.qr_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_image.url)
        return None
    
    def get_generated_latitude(self, obj):
        """Get latitude from generated location"""
        if obj.generated_location:
            return obj.generated_location.y
        return None
    
    def get_generated_longitude(self, obj):
        """Get longitude from generated location"""
        if obj.generated_location:
            return obj.generated_location.x
        return None
    
    def get_scanned_latitude(self, obj):
        """Get latitude from scanned location"""
        if obj.scanned_location:
            return obj.scanned_location.y
        return None
    
    def get_scanned_longitude(self, obj):
        """Get longitude from scanned location"""
        if obj.scanned_location:
            return obj.scanned_location.x
        return None
    
    def get_time_remaining(self, obj):
        """Get time remaining until expiry in minutes"""
        if obj.status == 'pending':
            from datetime import datetime
            now = datetime.now()
            expires = obj.expires_at.replace(tzinfo=None)
            if expires > now:
                diff = expires - now
                return int(diff.total_seconds() / 60)
        return 0


class QRScanSerializer(serializers.Serializer):
    """
    QR Code scan serializer
    """
    transaction_id = serializers.CharField()
    qr_hash = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    
    def validate(self, attrs):
        """Validate QR scan data"""
        try:
            transaction = QRTransaction.objects.get(
                transaction_id=attrs['transaction_id']
            )
            attrs['transaction'] = transaction
        except QRTransaction.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code")
        
        return attrs


class RewardTransactionSerializer(serializers.ModelSerializer):
    """
    Reward transaction serializer
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = RewardTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'description',
            'user_name', 'reference_id', 'created_at'
        ]


class CustomerVisitSerializer(serializers.ModelSerializer):
    """
    Customer visit serializer
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    visit_latitude = serializers.SerializerMethodField()
    visit_longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerVisit
        fields = [
            'id', 'visit_source', 'time_spent_seconds', 'customer_name',
            'shop_name', 'visit_latitude', 'visit_longitude', 'created_at'
        ]
    
    def get_visit_latitude(self, obj):
        if obj.visit_location:
            return obj.visit_location.y
        return None
    
    def get_visit_longitude(self, obj):
        if obj.visit_location:
            return obj.visit_location.x
        return None


class ReferralCodeSerializer(serializers.ModelSerializer):
    """
    Referral code serializer
    """
    referrer_name = serializers.CharField(source='referrer.full_name', read_only=True)
    can_be_used = serializers.ReadOnlyField()
    
    class Meta:
        model = ReferralCode
        fields = [
            'id', 'code', 'referrer_name', 'usage_count', 'max_usage',
            'referrer_reward', 'referee_reward', 'is_active', 'expires_at',
            'can_be_used', 'created_at'
        ]


class ReferralCodeCreateSerializer(serializers.ModelSerializer):
    """
    Referral code creation serializer
    """
    
    class Meta:
        model = ReferralCode
        fields = [
            'code', 'max_usage', 'referrer_reward', 'referee_reward', 'expires_at'
        ]
    
    def create(self, validated_data):
        """Create referral code with referrer from request"""
        validated_data['referrer'] = self.context['request'].user
        return super().create(validated_data)


class ReferralCodeUseSerializer(serializers.Serializer):
    """
    Referral code usage serializer
    """
    referral_code = serializers.CharField()
    
    def validate_referral_code(self, value):
        """Validate referral code"""
        try:
            code = ReferralCode.objects.get(code=value)
            if not code.can_be_used():
                raise serializers.ValidationError("Referral code cannot be used")
            return code
        except ReferralCode.DoesNotExist:
            raise serializers.ValidationError("Invalid referral code")