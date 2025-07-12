"""
URL patterns for Transaction and QR Code APIs
"""

from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # QR Code transactions
    path('qr/generate/', views.QRTransactionCreateView.as_view(), name='qr_generate'),
    path('qr/', views.QRTransactionListView.as_view(), name='qr_list'),
    path('qr/scan/', views.QRScanView.as_view(), name='qr_scan'),
    
    # Reward transactions
    path('rewards/', views.RewardTransactionListView.as_view(), name='rewards'),
    
    # Referral codes
    path('referrals/', views.ReferralCodeListCreateView.as_view(), name='referrals'),
    path('referrals/use/', views.ReferralCodeUseView.as_view(), name='use_referral'),
    
    # Analytics and utilities
    path('analytics/', views.transaction_analytics, name='analytics'),
    path('types/', views.transaction_types, name='types'),
]