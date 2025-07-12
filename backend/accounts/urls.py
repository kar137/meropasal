"""
URL patterns for Authentication APIs
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('signup/', views.UserRegistrationView.as_view(), name='signup'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('update-location/', views.UserLocationUpdateView.as_view(), name='update_location'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('stats/', views.user_stats, name='user_stats'),
    
    # Wallet endpoints
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('wallet/transactions/', views.WalletTransactionListView.as_view(), name='wallet_transactions'),
]