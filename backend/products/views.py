"""
Product Management Views for Pasale App
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404

from .models import (
    ProductCategory, Product, ProductImage, ProductStockMovement,
    ProductReview, ProductWishlist
)
from .serializers import (
    ProductCategorySerializer, ProductSerializer, ProductCreateUpdateSerializer,
    ProductImageSerializer, ProductStockMovementSerializer, ProductReviewSerializer,
    ProductWishlistSerializer, ProductSearchSerializer, ProductStockUpdateSerializer
)

class ProductCategoryListView(generics.ListAPIView):
    """
    Product Categories API
    GET /products/categories/
    
    Get list of all product categories
    """
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        """List product categories"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Product categories retrieved',
            'data': serializer.data
        })


class ProductListCreateView(generics.ListCreateAPIView):
    """
    Product List/Create API
    GET/POST /products/
    
    List products or create new product (shopkeepers only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get products based on user role"""
        if self.request.user.role == 'shopkeeper':
            # Shopkeepers see their own products
            try:
                return self.request.user.shop.products.all()
            except:
                return Product.objects.none()
        else:
            # Customers see all active products
            return Product.objects.filter(is_active=True, shop__is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def create(self, request, *args, **kwargs):
        """Create new product (shopkeepers only)"""
        if request.user.role != 'shopkeeper':
            return Response({
                'success': False,
                'message': 'Only shopkeepers can create products',
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
                product = serializer.save()
                
                # Update shop's total products count
                shop = request.user.shop
                shop.total_products = shop.products.filter(is_active=True).count()
                shop.save(update_fields=['total_products'])
                
                return Response({
                    'success': True,
                    'message': 'Product created successfully',
                    'data': ProductSerializer(product, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Product creation failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """List products with filters"""
        queryset = self.get_queryset()
        
        # Apply filters
        category = request.GET.get('category')
        search = request.GET.get('search', '').strip()
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        in_stock = request.GET.get('in_stock')
        featured = request.GET.get('featured')
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search) |
                Q(brand__icontains=search)
            )
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Order by
        order_by = request.GET.get('order_by', '-created_at')
        if order_by in ['price', '-price', 'name', '-name', 'created_at', '-created_at']:
            queryset = queryset.order_by(order_by)
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': f'Found {len(serializer.data)} products',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': f'Found {len(serializer.data)} products',
            'data': serializer.data
        })


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Product Detail API
    GET/PUT/DELETE /products/{product_id}/
    
    View, update, or delete product details
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get product details"""
        product = self.get_object()
        
        # Increment view count
        product.increment_view_count()
        
        serializer = self.get_serializer(product)
        return Response({
            'success': True,
            'message': 'Product details retrieved',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """Update product (owner only)"""
        product = self.get_object()
        
        # Check if user owns this product
        if product.shop.owner != request.user:
            return Response({
                'success': False,
                'message': 'You can only update your own products',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Product updated successfully',
                'data': ProductSerializer(product, context={'request': request}).data
            })
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete product (owner only)"""
        product = self.get_object()
        
        # Check if user owns this product
        if product.shop.owner != request.user:
            return Response({
                'success': False,
                'message': 'You can only delete your own products',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        product.delete()
        
        # Update shop's total products count
        shop = request.user.shop
        shop.total_products = shop.products.filter(is_active=True).count()
        shop.save(update_fields=['total_products'])
        
        return Response({
            'success': True,
            'message': 'Product deleted successfully',
            'data': None
        })


class ProductSearchView(APIView):
    """
    Product Search API
    GET /products/search/
    
    Search products by location and query
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Search products near user location"""
        try:
            # Get user location
            user_location = request.user.location
            if not user_location:
                return Response({
                    'success': False,
                    'message': 'User location not available. Please update your location.',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get search parameters
            query = request.GET.get('query', '').strip()
            radius_km = float(request.GET.get('radius', 10))  # Default 10km
            category = request.GET.get('category')
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            in_stock_only = request.GET.get('in_stock', 'true') == 'true'
            
            if not query:
                return Response({
                    'success': False,
                    'message': 'Search query is required',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find products in nearby shops
            products = Product.objects.filter(
                is_active=True,
                shop__is_active=True,
                shop__location__distance_lte=(user_location, Distance(km=radius_km))
            ).filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query) |
                Q(brand__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('shop', 'category')
            
            # Apply additional filters
            if category:
                products = products.filter(category__name__icontains=category)
            
            if min_price:
                try:
                    products = products.filter(price__gte=float(min_price))
                except ValueError:
                    pass
            
            if max_price:
                try:
                    products = products.filter(price__lte=float(max_price))
                except ValueError:
                    pass
            
            if in_stock_only:
                products = products.filter(stock_quantity__gt=0)
            
            # Order by shop distance
            products = products.annotate(
                shop_distance=Distance('shop__location', user_location)
            ).order_by('shop_distance', 'price')
            
            # Limit results
            products = products[:100]
            
            # Serialize results
            serializer = ProductSearchSerializer(
                products,
                many=True,
                context={'user_location': user_location}
            )
            
            return Response({
                'success': True,
                'message': f'Found {len(serializer.data)} products for "{query}"',
                'data': {
                    'products': serializer.data,
                    'search_params': {
                        'query': query,
                        'radius_km': radius_km,
                        'category': category,
                        'results_count': len(serializer.data)
                    }
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Search failed: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductStockUpdateView(APIView):
    """
    Product Stock Update API
    POST /products/{product_id}/stock/
    
    Update product stock (shopkeepers only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_id):
        """Update product stock"""
        if request.user.role != 'shopkeeper':
            return Response({
                'success': False,
                'message': 'Only shopkeepers can update stock',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user owns this product
        if product.shop.owner != request.user:
            return Response({
                'success': False,
                'message': 'You can only update stock for your own products',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductStockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                old_stock = product.stock_quantity
                serializer.update(product, serializer.validated_data)
                
                return Response({
                    'success': True,
                    'message': 'Stock updated successfully',
                    'data': {
                        'product_id': str(product.id),
                        'old_stock': old_stock,
                        'new_stock': product.stock_quantity,
                        'change': serializer.validated_data['quantity_change']
                    }
                })
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Stock update failed: {str(e)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewView(generics.ListCreateAPIView):
    """
    Product Review API
    GET/POST /products/{product_id}/reviews/
    
    View and create product reviews
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product'] = get_object_or_404(Product, id=self.kwargs['product_id'])
        return context
    
    def create(self, request, *args, **kwargs):
        """Create product review (customers only)"""
        if request.user.role != 'customer':
            return Response({
                'success': False,
                'message': 'Only customers can review products',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        product = get_object_or_404(Product, id=kwargs['product_id'])
        
        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(
            product=product,
            customer=request.user
        ).first()
        
        if existing_review:
            # Update existing review
            serializer = self.get_serializer(existing_review, data=request.data, partial=True)
        else:
            # Create new review
            serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Review submitted successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Invalid review data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductWishlistView(generics.ListCreateDestroyAPIView):
    """
    Product Wishlist API
    GET/POST/DELETE /products/wishlist/
    
    Manage customer wishlist
    """
    serializer_class = ProductWishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProductWishlist.objects.filter(customer=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Add product to wishlist"""
        if request.user.role != 'customer':
            return Response({
                'success': False,
                'message': 'Only customers can have wishlists',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'success': False,
                'message': 'Product ID is required',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item, created = ProductWishlist.objects.get_or_create(
            customer=request.user,
            product=product
        )
        
        if created:
            serializer = self.get_serializer(wishlist_item)
            return Response({
                'success': True,
                'message': f'{product.name} added to wishlist',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': True,
                'message': f'{product.name} is already in your wishlist',
                'data': None
            })
    
    def delete(self, request, *args, **kwargs):
        """Remove product from wishlist"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'success': False,
                'message': 'Product ID is required',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist_item = ProductWishlist.objects.get(
                customer=request.user,
                product_id=product_id
            )
            product_name = wishlist_item.product.name
            wishlist_item.delete()
            
            return Response({
                'success': True,
                'message': f'{product_name} removed from wishlist',
                'data': None
            })
            
        except ProductWishlist.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found in wishlist',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_analytics(request, product_id):
    """
    Product Analytics API
    GET /products/{product_id}/analytics/
    
    Get product analytics (owner only)
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user owns this product
    if product.shop.owner != request.user:
        return Response({
            'success': False,
            'message': 'You can only view analytics for your own products',
            'data': None
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from datetime import datetime, timedelta
        
        # Calculate analytics
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        analytics = {
            'overview': {
                'total_views': product.view_count,
                'total_orders': product.order_count,
                'current_stock': product.stock_quantity,
                'is_low_stock': product.is_low_stock,
                'average_rating': product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
                'total_reviews': product.reviews.count(),
            },
            'recent_activity': {
                'views_this_week': product.stock_movements.filter(
                    created_at__date__gte=week_ago
                ).count(),
                'stock_movements_this_month': product.stock_movements.filter(
                    created_at__date__gte=month_ago
                ).count(),
                'reviews_this_month': product.reviews.filter(
                    created_at__date__gte=month_ago
                ).count(),
            },
            'stock_history': [
                {
                    'date': movement.created_at.strftime('%Y-%m-%d'),
                    'type': movement.movement_type,
                    'change': movement.quantity_change,
                    'new_level': movement.new_stock_level,
                    'reason': movement.reason
                }
                for movement in product.stock_movements.all()[:10]
            ]
        }
        
        return Response({
            'success': True,
            'message': 'Product analytics retrieved',
            'data': analytics
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get analytics: {str(e)}',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)