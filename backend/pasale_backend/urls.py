"""
Main URL configuration for Pasale Backend
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root endpoint
    Provides information about available API endpoints
    """
    return Response({
        'message': 'Welcome to Pasale API - Hyperlocal Retail Platform for Nepal',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'shops': '/api/shops/',
            'products': '/api/products/',
            'transactions': '/api/transactions/',
            'verification': '/api/verification/',
            'analytics': '/api/analytics/',
        },
        'documentation': '/api/docs/',
        'admin': '/admin/',
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API root
    path('api/', api_root, name='api_root'),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/shops/', include('shops.urls')),
    path('api/products/', include('products.urls')),
    path('api/transactions/', include('transactions.urls')),
    # path('api/verification/', include('verification.urls')),
    # path('api/analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)