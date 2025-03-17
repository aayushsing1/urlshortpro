from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_url, name='create_url'),
    path('stats/<str:short_code>/', views.url_stats, name='url_stats'),
    path('<str:short_code>/', views.redirect_to_url, name='redirect'),
    path('<str:short_code>/1/', views.interstitial1, name='interstitial1'),
    path('<str:short_code>/2/', views.interstitial2, name='interstitial2'),
    path('<str:short_code>/go/', views.final_redirect, name='final_redirect'),
]