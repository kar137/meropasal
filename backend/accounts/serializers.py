"""
Serializers for User Authentication API
Handles registration, login, and profile management
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.gis.geos import Point
from .models import User, UserWallet, WalletTransaction

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    Supports both customer and shopkeeper registration
    """
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'full_name', 'phone_number', 'role', 'address', 'city',
            'language_preference', 'latitude', 'longitude'
        ]
    
    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if phone number already exists
        if User.objects.filter(phone_number=attrs['phone_number']).exists():
            raise serializers.ValidationError("Phone number already registered")
        
        return attrs
    
    def create(self, validated_data):
        """Create new user with wallet"""
        # Remove password_confirm and location data
        validated_data.pop('password_confirm')
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Set location if provided
        if latitude and longitude:
            user.location = Point(longitude, latitude)
            user.save()
        
        # Create wallet for user
        UserWallet.objects.create(user=user)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer
    Returns user data along with tokens
    """
    
    def validate(self, attrs):
        """Validate login credentials"""
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'full_name': self.user.full_name,
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            'role': self.user.role,
            'is_verified': self.user.is_verified,
            'profile_image': self.user.profile_image.url if self.user.profile_image else None,
            'language_preference': self.user.language_preference,
            'notifications_enabled': self.user.notifications_enabled,
        }
        
        # Add wallet balance
        try:
            wallet = self.user.wallet
            data['user']['wallet_balance'] = wallet.balance
        except UserWallet.DoesNotExist:
            # Create wallet if doesn't exist
            wallet = UserWallet.objects.create(user=self.user)
            data['user']['wallet_balance'] = 0
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer for viewing and updating profile
    """
    wallet_balance = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'role', 'profile_image', 'address', 'city', 'language_preference',
            'notifications_enabled', 'is_verified', 'wallet_balance',
            'latitude', 'longitude', 'created_at', 'last_active'
        ]
        read_only_fields = ['id', 'role', 'is_verified', 'created_at']
    
    def get_wallet_balance(self, obj):
        """Get user's wallet balance"""
        try:
            return obj.wallet.balance
        except UserWallet.DoesNotExist:
            return 0
    
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


class UserLocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating user location
    """
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    address = serializers.CharField(max_length=500, required=False)
    
    def update(self, instance, validated_data):
        """Update user location"""
        latitude = validated_data['latitude']
        longitude = validated_data['longitude']
        
        instance.location = Point(longitude, latitude)
        if 'address' in validated_data:
            instance.address = validated_data['address']
        
        instance.save()
        return instance


class WalletSerializer(serializers.ModelSerializer):
    """
    Wallet serializer for wallet information
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserWallet
        fields = [
            'balance', 'total_earned', 'total_spent',
            'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['balance', 'total_earned', 'total_spent', 'created_at', 'updated_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    Wallet transaction serializer for transaction history
    """
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'reason',
            'balance_after', 'created_at'
        ]
        read_only_fields = ['id', 'balance_after', 'created_at']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value