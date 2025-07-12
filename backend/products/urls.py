"""
URL patterns for Product Management APIs
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product categories
    path('categories/', views.ProductCategoryListView.as_view(), name='categories'),
    
    # Product management
    path('', views.ProductListCreateView.as_view(), name='list_create'),
    path('<uuid:pk>/', views.ProductDetailView.as_view(), name='detail'),
    path('<uuid:product_id>/analytics/', views.product_analytics, name='analytics'),
    
    # Product search
    path('search/', views.ProductSearchView.as_view(), name='search'),
    
    # Stock management
    path('<uuid:product_id>/stock/', views.ProductStockUpdateView.as_view(), name='stock_update'),
    
    # Product interactions
    path('<uuid:product_id>/reviews/', views.ProductReviewView.as_view(), name='reviews'),
    path('wishlist/', views.ProductWishlistView.as_view(), name='wishlist'),
]