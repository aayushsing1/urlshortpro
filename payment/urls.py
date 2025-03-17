from django.urls import path
from . import views

urlpatterns = [
    path('earnings/', views.earnings_dashboard, name='earnings_dashboard'),
    path('withdrawal/', views.withdrawal_request, name='withdrawal_request'),
    path('earnings/history/', views.earnings_history, name='earnings_history'),
    path('transactions/', views.transaction_history, name='transaction_history'),
]