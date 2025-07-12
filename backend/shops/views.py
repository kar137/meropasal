"""
Shop Management Views for Pasale App
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404

from .models import Shop, ShopImage, ShopRating, ShopVisit, ShopFollower
from .serializers import (
    ShopRegistrationSerializer,
    ShopSerializer,
    ShopUpdateSerializer,
    ShopImageSerializer,
    ShopRatingSerializer,
    ShopVisitSerializer,
    ShopFollowerSerializer,
    NearbyShopSerializer
)

class ShopRegistrationView(generics.CreateAPIView):
    """
    Shop Registration API
    POST /shops/register/
    
    Register new shop for shopkeepers
    """
    serializer_class = ShopRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Handle shop registration"""
        # Check if user is shopkeeper
        if request.user.role != 'shopkeeper':
            return Response({
                'success': False,
                'message': 'Only shopkeepers can register shops',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user already has a shop
        if hasattr(request.user, 'shop'):
            return Response({
                'success': False,
                'message': 'You already have a registered shop',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                shop = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Shop registered successfully! Verification pending.',
                    'data': {
                        'shop_id': str(shop.id),
                        'shop_name': shop.name,
                        'is_verified': shop.is_verified
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Shop registration failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Shop Detail API
    GET/PUT/DELETE /shops/{shop_id}/
    
    View, update, or delete shop details
    """
    queryset = Shop.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ShopUpdateSerializer
        return ShopSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add user location for distance calculation
        if self.request.user.location:
            context['user_location'] = self.request.user.location
        return context
    
    def update(self, request, *args, **kwargs):
        """Update shop details"""
        shop = self.get_object()
        
        # Check if user owns this shop
        if shop.owner != request.user:
            return Response({
                'success': False,
                'message': 'You can only update your own shop',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(shop, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Shop updated successfully',
                'data': ShopSerializer(shop, context=self.get_serializer_context()).data
            })
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """Get shop details"""
        shop = self.get_object()
        
        # Increment visit count if customer is viewing
        if request.user.is_customer and request.user.location:
            ShopVisit.objects.create(
                shop=shop,
                customer=request.user,
                visit_location=request.user.location,
                visit_type='browse'
            )
            shop.increment_visit_count()
        
        serializer = self.get_serializer(shop)
        return Response({
            'success': True,
            'message': 'Shop details retrieved',
            'data': serializer.data
        })


class NearbyShopsView(APIView):
    """
    Nearby Shops Search API
    GET /shops/nearby/
    
    Find shops near user's location with optional filters
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Search for nearby shops"""
        try:
            # Get user location
            user_location = request.user.location
            if not user_location:
                return Response({
                    'success': False,
                    'message': 'User location not available. Please update your location.',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get query parameters
            radius_km = float(request.GET.get('radius', 5))  # Default 5km radius
            category = request.GET.get('category')
            search_query = request.GET.get('query', '').strip()
            is_verified = request.GET.get('verified')
            is_open = request.GET.get('open')
            
            # Build query
            shops = Shop.objects.filter(
                is_active=True,
                location__distance_lte=(user_location, Distance(km=radius_km))
            ).annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')
            
            # Apply filters
            if category:
                shops = shops.filter(category=category)
            
            if search_query:
                shops = shops.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__icontains=search_query)
                )
            
            if is_verified == 'true':
                shops = shops.filter(is_verified=True)
            
            if is_open == 'true':
                from datetime import datetime
                current_time = datetime.now().time()
                shops = shops.filter(
                    Q(is_open_24_7=True) |
                    Q(opening_time__lte=current_time, closing_time__gte=current_time)
                )
            
            # Serialize results
            serializer = NearbyShopSerializer(
                shops[:50],  # Limit to 50 results
                many=True,
                context={'user_location': user_location}
            )
            
            return Response({
                'success': True,
                'message': f'Found {len(serializer.data)} shops nearby',
                'data': {
                    'shops': serializer.data,
                    'search_params': {
                        'radius_km': radius_km,
                        'category': category,
                        'query': search_query,
                        'user_location': {
                            'latitude': user_location.y,
                            'longitude': user_location.x
                        }
                    }
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Search failed: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)


class ShopRatingView(generics.ListCreateAPIView):
    """
    Shop Rating API
    GET/POST /shops/{shop_id}/ratings/
    
    View and create shop ratings
    """
    serializer_class = ShopRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        return ShopRating.objects.filter(shop_id=shop_id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['shop'] = get_object_or_404(Shop, id=self.kwargs['shop_id'])
        return context
    
    def create(self, request, *args, **kwargs):
        """Create shop rating"""
        if request.user.role != 'customer':
            return Response({
                'success': False,
                'message': 'Only customers can rate shops',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        shop = get_object_or_404(Shop, id=kwargs['shop_id'])
        
        # Check if user already rated this shop
        existing_rating = ShopRating.objects.filter(
            shop=shop,
            customer=request.user
        ).first()
        
        if existing_rating:
            # Update existing rating
            serializer = self.get_serializer(existing_rating, data=request.data, partial=True)
        else:
            # Create new rating
            serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Rating submitted successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Invalid rating data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """List shop ratings"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Ratings retrieved',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Ratings retrieved',
            'data': serializer.data
        })


class ShopFollowView(APIView):
    """
    Shop Follow/Unfollow API
    POST /shops/{shop_id}/follow/
    DELETE /shops/{shop_id}/follow/
    
    Follow or unfollow a shop
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, shop_id):
        """Follow a shop"""
        if request.user.role != 'customer':
            return Response({
                'success': False,
                'message': 'Only customers can follow shops',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        shop = get_object_or_404(Shop, id=shop_id)
        
        follower, created = ShopFollower.objects.get_or_create(
            shop=shop,
            customer=request.user
        )
        
        if created:
            return Response({
                'success': True,
                'message': f'You are now following {shop.name}',
                'data': {'is_following': True}
            })
        else:
            return Response({
                'success': True,
                'message': f'You are already following {shop.name}',
                'data': {'is_following': True}
            })
    
    def delete(self, request, shop_id):
        """Unfollow a shop"""
        shop = get_object_or_404(Shop, id=shop_id)
        
        try:
            follower = ShopFollower.objects.get(
                shop=shop,
                customer=request.user
            )
            follower.delete()
            
            return Response({
                'success': True,
                'message': f'You unfollowed {shop.name}',
                'data': {'is_following': False}
            })
            
        except ShopFollower.DoesNotExist:
            return Response({
                'success': True,
                'message': f'You were not following {shop.name}',
                'data': {'is_following': False}
            })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_shop(request):
    """
    My Shop API
    GET /shops/my-shop/
    
    Get current user's shop details
    """
    if request.user.role != 'shopkeeper':
        return Response({
            'success': False,
            'message': 'Only shopkeepers can access this endpoint',
            'data': None
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        shop = request.user.shop
        serializer = ShopSerializer(shop, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Shop details retrieved',
            'data': serializer.data
        })
        
    except Shop.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No shop registered. Please register your shop first.',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def shop_analytics(request, shop_id):
    """
    Shop Analytics API
    GET /shops/{shop_id}/analytics/
    
    Get shop analytics and statistics
    """
    shop = get_object_or_404(Shop, id=shop_id)
    
    # Check if user owns this shop
    if shop.owner != request.user:
        return Response({
            'success': False,
            'message': 'You can only view analytics for your own shop',
            'data': None
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from datetime import datetime, timedelta
        from django.db.models import Count, Avg
        
        # Calculate analytics
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        analytics = {
            'overview': {
                'total_visits': shop.total_visits,
                'total_products': shop.products.count(),
                'total_followers': shop.followers.count(),
                'average_rating': float(shop.average_rating),
                'total_ratings': shop.ratings.count(),
            },
            'recent_activity': {
                'visits_this_week': shop.visits.filter(created_at__date__gte=week_ago).count(),
                'visits_this_month': shop.visits.filter(created_at__date__gte=month_ago).count(),
                'new_followers_this_week': shop.followers.filter(created_at__date__gte=week_ago).count(),
                'new_ratings_this_week': shop.ratings.filter(created_at__date__gte=week_ago).count(),
            },
            'ratings_breakdown': {
                'five_star': shop.ratings.filter(rating=5).count(),
                'four_star': shop.ratings.filter(rating=4).count(),
                'three_star': shop.ratings.filter(rating=3).count(),
                'two_star': shop.ratings.filter(rating=2).count(),
                'one_star': shop.ratings.filter(rating=1).count(),
            }
        }
        
        return Response({
            'success': True,
            'message': 'Shop analytics retrieved',
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
def shop_categories(request):
    """
    Shop Categories API
    GET /shops/categories/
    
    Get list of available shop categories
    """
    categories = [
        {'value': choice[0], 'label': choice[1]}
        for choice in Shop.CATEGORY_CHOICES
    ]
    
    return Response({
        'success': True,
        'message': 'Shop categories retrieved',
        'data': categories
    })