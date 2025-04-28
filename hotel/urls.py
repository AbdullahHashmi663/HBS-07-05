from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),
    
    # Room Type URLs
    path('room-types/', views.room_type_list, name='room_type_list'),
    path('room-types/create/', views.room_type_create, name='room_type_create'),
    path('room-types/<int:pk>/edit/', views.room_type_edit, name='room_type_edit'),
    path('room-types/<int:pk>/delete/', views.room_type_delete, name='room_type_delete'),
    
    # Room URLs
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
    
    # Guest URLs
    path('guests/', views.guest_list, name='guest_list'),
    path('guests/create/', views.guest_create, name='guest_create'),
    path('guests/<int:pk>/edit/', views.guest_edit, name='guest_edit'),
    path('guests/<int:pk>/delete/', views.guest_delete, name='guest_delete'),
    path('guests/<int:pk>/', views.guest_detail, name='guest_detail'),
    
    # Booking URLs
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('bookings/<int:pk>/pdf/', views.booking_receipt_pdf, name='booking_receipt_pdf'),
    path('check-availability/', views.check_room_availability, name='check_room_availability'),
    
    # User Management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/activate/', views.user_activate, name='user_activate'),
    path('users/<int:pk>/deactivate/', views.user_deactivate, name='user_deactivate'),
    
    # Reports URLs
    path('reports/', views.reports, name='reports'),
    path('reports/occupancy/', views.occupancy_report, name='occupancy_report'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    
    # Theme Settings URL
    path('settings/theme/', views.theme_settings, name='theme_settings'),
] 