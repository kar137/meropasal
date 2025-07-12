"""
Transaction and QR Code Views for Pasale App
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta

from .models import QRTransaction, RewardTransaction, CustomerVisit, ReferralCode
from .serializers import (
    QRTransactionCreateSerializer, QRTransactionSerializer, QRScanSerializer,
    RewardTransactionSerializer, CustomerVisitSerializer, ReferralCodeSerializer,
    ReferralCodeCreateSerializer, ReferralCodeUseSerializer
)

class QRTransactionCreateView(generics.CreateAPIView):
    """
    QR Transaction Creation API
    POST /transactions/qr/generate/
    
    Generate QR code for shop visits and rewards (shopkeepers only)
    """
    serializer_class = QRTransactionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Generate QR code transaction"""
        if request.user.role != 'shopkeeper':
            return Response({
                'success': False,
                'message': 'Only shopkeepers can generate QR codes',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user has a shop
        if not hasattr(request.user, 'shop'):
            return Response({
                'success': False,
                'message': 'Please register your shop first',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                qr_transaction = serializer.save()
                
                # Return QR transaction details
                response_serializer = QRTransactionSerializer(
                    qr_transaction,
                    context={'request': request}
                )
                
                return Response({
                    'success': True,
                    'message': 'QR code generated successfully',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'QR generation failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class QRTransactionListView(generics.ListAPIView):
    """
    QR Transaction List API
    GET /transactions/qr/
    
    List QR transactions for current user
    """
    serializer_class = QRTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get QR transactions based on user role"""
        user = self.request.user
        
        if user.role == 'shopkeeper':
            # Shopkeepers see their shop's QR transactions
            try:
                return user.shop.qr_transactions.all()
            except:
                return QRTransaction.objects.none()
        else:
            # Customers see their scanned QR transactions
            return user.qr_transactions.all()
    
    def list(self, request, *args, **kwargs):
        """List QR transactions with filters"""
        queryset = self.get_queryset()
        
        # Apply filters
        status_filter = request.GET.get('status')
        transaction_type = request.GET.get('type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(generated_at__date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(generated_at__date__lte=to_date)
            except ValueError:
                pass
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'QR transactions retrieved',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'QR transactions retrieved',
            'data': serializer.data
        })


class QRScanView(APIView):
    """
    QR Code Scan API
    POST /transactions/qr/scan/
    
    Scan and verify QR code (customers only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Scan QR code"""
        if request.user.role != 'customer':
            return Response({
                'success': False,
                'message': 'Only customers can scan QR codes',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = QRScanSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                transaction = serializer.validated_data['transaction']
                qr_hash = serializer.validated_data['qr_hash']
                latitude = serializer.validated_data['latitude']
                longitude = serializer.validated_data['longitude']
                
                scan_location = Point(longitude, latitude)
                
                # Verify scan
                success, message = transaction.verify_scan(
                    customer=request.user,
                    scan_location=scan_location,
                    scanned_hash=qr_hash
                )
                
                if success:
                    # Create customer visit record
                    CustomerVisit.objects.create(
                        customer=request.user,
                        shop=transaction.shop,
                        visit_location=scan_location,
                        visit_source='qr_scan'
                    )
                    
                    response_data = {
                        'transaction_id': transaction.transaction_id,
                        'shop_name': transaction.shop.name,
                        'reward_earned': transaction.reward_amount,
                        'new_wallet_balance': request.user.wallet.balance
                    }
                    
                    return Response({
                        'success': True,
                        'message': message,
                        'data': response_data
                    })
                else:
                    return Response({
                        'success': False,
                        'message': message,
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'QR scan failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid QR data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RewardTransactionListView(generics.ListAPIView):
    """
    Reward Transaction List API
    GET /transactions/rewards/
    
    List reward transactions for current user
    """
    serializer_class = RewardTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's reward transactions"""
        return self.request.user.reward_transactions.all()
    
    def list(self, request, *args, **kwargs):
        """List reward transactions with filters"""
        queryset = self.get_queryset()
        
        # Apply filters
        transaction_type = request.GET.get('type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=to_date)
            except ValueError:
                pass
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Reward transactions retrieved',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Reward transactions retrieved',
            'data': serializer.data
        })


class ReferralCodeListCreateView(generics.ListCreateAPIView):
    """
    Referral Code API
    GET/POST /transactions/referrals/
    
    List and create referral codes
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's referral codes"""
        return self.request.user.referral_codes.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReferralCodeCreateSerializer
        return ReferralCodeSerializer
    
    def create(self, request, *args, **kwargs):
        """Create referral code"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                referral_code = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Referral code created successfully',
                    'data': ReferralCodeSerializer(referral_code).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Referral code creation failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """List referral codes"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Referral codes retrieved',
            'data': serializer.data
        })


class ReferralCodeUseView(APIView):
    """
    Use Referral Code API
    POST /transactions/referrals/use/
    
    Use a referral code to get rewards
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Use referral code"""
        serializer = ReferralCodeUseSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                referral_code = serializer.validated_data['referral_code']
                
                success, message = referral_code.use_code(request.user)
                
                if success:
                    return Response({
                        'success': True,
                        'message': message,
                        'data': {
                            'referral_code': referral_code.code,
                            'reward_earned': referral_code.referee_reward,
                            'new_wallet_balance': request.user.wallet.balance
                        }
                    })
                else:
                    return Response({
                        'success': False,
                        'message': message,
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Referral code usage failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid referral code',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def transaction_analytics(request):
    """
    Transaction Analytics API
    GET /transactions/analytics/
    
    Get transaction analytics for current user
    """
    user = request.user
    
    try:
        # Calculate date ranges
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        analytics = {
            'overview': {
                'total_rewards_earned': user.reward_transactions.filter(
                    amount__gt=0
                ).aggregate(Sum('amount'))['amount__sum'] or 0,
                'total_rewards_spent': abs(user.reward_transactions.filter(
                    amount__lt=0
                ).aggregate(Sum('amount'))['amount__sum'] or 0),
                'current_wallet_balance': user.wallet.balance,
            },
            'recent_activity': {
                'rewards_this_week': user.reward_transactions.filter(
                    created_at__date__gte=week_ago,
                    amount__gt=0
                ).aggregate(Sum('amount'))['amount__sum'] or 0,
                'rewards_this_month': user.reward_transactions.filter(
                    created_at__date__gte=month_ago,
                    amount__gt=0
                ).aggregate(Sum('amount'))['amount__sum'] or 0,
            }
        }
        
        # Add role-specific analytics
        if user.role == 'shopkeeper':
            try:
                shop = user.shop
                analytics['shop'] = {
                    'total_qr_generated': shop.qr_transactions.count(),
                    'total_qr_scanned': shop.qr_transactions.filter(status='verified').count(),
                    'total_customer_visits': shop.customer_visits.count(),
                    'visits_this_week': shop.customer_visits.filter(
                        created_at__date__gte=week_ago
                    ).count(),
                    'visits_this_month': shop.customer_visits.filter(
                        created_at__date__gte=month_ago
                    ).count(),
                }
            except:
                analytics['shop'] = None
        
        elif user.role == 'customer':
            analytics['customer'] = {
                'total_qr_scanned': user.qr_transactions.filter(status='verified').count(),
                'total_shop_visits': user.visits.count(),
                'unique_shops_visited': user.visits.values('shop').distinct().count(),
                'visits_this_week': user.visits.filter(
                    created_at__date__gte=week_ago
                ).count(),
                'visits_this_month': user.visits.filter(
                    created_at__date__gte=month_ago
                ).count(),
            }
        
        return Response({
            'success': True,
            'message': 'Transaction analytics retrieved',
            'data': analytics
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get analytics: {str(e)}',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def transaction_types(request):
    """
    Transaction Types API
    GET /transactions/types/
    
    Get available transaction types
    """
    types = {
        'qr_transaction_types': [
            {'value': choice[0], 'label': choice[1]}
            for choice in QRTransaction.TRANSACTION_TYPES
        ],
        'reward_transaction_types': [
            {'value': choice[0], 'label': choice[1]}
            for choice in RewardTransaction.TRANSACTION_TYPES
        ],
        'qr_status_types': [
            {'value': choice[0], 'label': choice[1]}
            for choice in QRTransaction.STATUS_CHOICES
        ]
    }
    
    return Response({
        'success': True,
        'message': 'Transaction types retrieved',
        'data': types
    })