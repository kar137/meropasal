"""
Authentication Views for Pasale App
Handles user registration, login, profile management
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db import transaction

from .models import User, UserWallet, WalletTransaction
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserLocationUpdateSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
    PasswordChangeSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """
    User Registration API
    POST /auth/signup
    
    Supports both customer and shopkeeper registration
    Creates user account with digital wallet
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle user registration"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Return success response
                    return Response({
                        'success': True,
                        'message': 'Registration successful! Please login to continue.',
                        'data': {
                            'user_id': str(user.id),
                            'username': user.username,
                            'role': user.role,
                            'full_name': user.full_name
                        }
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Registration failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login API
    POST /auth/login
    
    Returns JWT tokens with user data
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle user login"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'data': serializer.validated_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Invalid credentials',
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User Profile API
    GET/PUT /auth/profile
    
    View and update user profile information
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLocationUpdateView(APIView):
    """
    Update User Location API
    POST /auth/update-location
    
    Updates user's current location coordinates
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Update user location"""
        serializer = UserLocationUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.update(request.user, serializer.validated_data)
                
                return Response({
                    'success': True,
                    'message': 'Location updated successfully',
                    'data': {
                        'latitude': serializer.validated_data['latitude'],
                        'longitude': serializer.validated_data['longitude']
                    }
                })
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Failed to update location: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid location data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class WalletView(generics.RetrieveAPIView):
    """
    User Wallet API
    GET /wallet/
    
    Get user's wallet information and balance
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create user wallet"""
        wallet, created = UserWallet.objects.get_or_create(user=self.request.user)
        return wallet
    
    def retrieve(self, request, *args, **kwargs):
        """Get wallet information"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'message': 'Wallet information retrieved',
            'data': serializer.data
        })


class WalletTransactionListView(generics.ListAPIView):
    """
    Wallet Transaction History API
    GET /wallet/transactions/
    
    Get user's wallet transaction history
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's wallet transactions"""
        try:
            wallet = self.request.user.wallet
            return wallet.transactions.all()
        except UserWallet.DoesNotExist:
            return WalletTransaction.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List wallet transactions"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Transaction history retrieved',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Transaction history retrieved',
            'data': serializer.data
        })


class PasswordChangeView(APIView):
    """
    Password Change API
    POST /auth/change-password
    
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                user = request.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # Keep user logged in after password change
                update_session_auth_hash(request, user)
                
                return Response({
                    'success': True,
                    'message': 'Password changed successfully',
                    'data': None
                })
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Failed to change password: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    User Statistics API
    GET /auth/stats
    
    Get user statistics and activity summary
    """
    user = request.user
    
    try:
        # Get wallet information
        wallet = user.wallet
        
        # Calculate statistics
        stats = {
            'profile': {
                'full_name': user.full_name,
                'role': user.get_role_display(),
                'is_verified': user.is_verified,
                'member_since': user.created_at.strftime('%Y-%m-%d'),
                'last_active': user.last_active.strftime('%Y-%m-%d %H:%M'),
            },
            'wallet': {
                'current_balance': wallet.balance,
                'total_earned': wallet.total_earned,
                'total_spent': wallet.total_spent,
                'transaction_count': wallet.transactions.count(),
            },
            'activity': {
                'total_sessions': user.sessions.count(),
                'active_sessions': user.sessions.filter(is_active=True).count(),
            }
        }
        
        # Add role-specific stats
        if user.is_shopkeeper:
            from shops.models import Shop
            try:
                shop = user.shop
                stats['shop'] = {
                    'shop_name': shop.name,
                    'is_verified': shop.is_verified,
                    'total_products': shop.products.count(),
                    'total_visits': shop.visits.count(),
                }
            except Shop.DoesNotExist:
                stats['shop'] = None
        
        return Response({
            'success': True,
            'message': 'User statistics retrieved',
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get statistics: {str(e)}',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout API
    POST /auth/logout
    
    Logout user and invalidate session
    """
    try:
        # Update user's last active time
        user = request.user
        user.save(update_fields=['last_active'])
        
        # Mark active sessions as inactive
        user.sessions.filter(is_active=True).update(is_active=False)
        
        return Response({
            'success': True,
            'message': 'Logged out successfully',
            'data': None
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Logout failed: {str(e)}',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)