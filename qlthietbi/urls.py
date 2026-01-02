from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quet-ma/', views.scan, name='scan'),
    path('thiet-bi/<str:qr_code>/', views.device_detail, name='device_detail'),
    path('ghi-nhat-ky/<str:qr_code>/', views.log_entry, name='log_entry'),
    path('lich-su/', views.history, name='history'),
]
