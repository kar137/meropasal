"""
URL patterns for Shop Management APIs
"""

from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    # Shop management
    path('register/', views.ShopRegistrationView.as_view(), name='register'),
    path('my-shop/', views.my_shop, name='my_shop'),
    path('categories/', views.shop_categories, name='categories'),
    
    # Shop discovery
    path('nearby/', views.NearbyShopsView.as_view(), name='nearby'),
    
    # Shop details
    path('<uuid:pk>/', views.ShopDetailView.as_view(), name='detail'),
    path('<uuid:shop_id>/analytics/', views.shop_analytics, name='analytics'),
    
    # Shop interactions
    path('<uuid:shop_id>/ratings/', views.ShopRatingView.as_view(), name='ratings'),
    path('<uuid:shop_id>/follow/', views.ShopFollowView.as_view(), name='follow'),
]