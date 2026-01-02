from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quet-ma/', views.scan, name='scan'),
    path('offline/', views.offline, name='offline'),
    path('thiet-bi/<str:qr_code>/', views.device_detail, name='device_detail'),
    path('ghi-nhat-ky/<str:qr_code>/', views.log_entry, name='log_entry'),
    path('api/ghi-nhat-ky/<str:qr_code>/', views.api_log_entry, name='api_log_entry'),
    path('lich-su/', views.history, name='history'),
]
