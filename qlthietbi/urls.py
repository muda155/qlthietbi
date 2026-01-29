from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quet-ma/', views.scan, name='scan'),
    path('offline/', views.offline, name='offline'),
    path('thiet-bi/<str:qr_code>/', views.device_detail, name='device_detail'),
    path('ghi-nhat-ky/<str:qr_code>/', views.log_entry, name='log_entry'),
    path('api/ghi-nhat-ky/<str:qr_code>/', views.api_log_entry, name='api_log_entry'),
    path('duyet/<int:log_id>/', views.approve_log, name='approve_log'),
    path('tu-choi/<int:log_id>/', views.reject_log, name='reject_log'),
    path('lich-su/', views.history, name='history'),
    
    # Maintenance URLs
    path('bao-duong/tao/<str:qr_code>/', views.create_maintenance_order, name='create_maintenance'),
    path('bao-duong/', views.maintenance_list, name='maintenance_list'),
    path('bao-duong/<int:order_id>/', views.maintenance_detail, name='maintenance_detail'),
    path('bao-duong/<int:order_id>/cap-nhat/', views.update_maintenance_order, name='update_maintenance'),
    path('bao-duong/<int:order_id>/hoan-thanh/', views.complete_maintenance_order, name='complete_maintenance'),
]
