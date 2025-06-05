from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Basic Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='hall_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hall_app/logout.html'), name='logout'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='hall_app/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='hall_app/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='hall_app/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='hall_app/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Hall Management
    path('halls/', views.hall_list, name='hall_list'),
    path('halls/<str:hall_id>/', views.hall_detail, name='hall_detail'),
    path('halls/create/', views.hall_create, name='hall_create'),
    path('halls/<str:hall_id>/update/', views.hall_update, name='hall_update'),
    path('halls/<str:hall_id>/delete/', views.hall_delete, name='hall_delete'),
    
    # Booking Management
    path('bookings/create/<str:hall_id>/', views.booking_create, name='booking_create'),
    path('bookings/payment/<str:booking_id>/', views.booking_payment, name='booking_payment'),
    path('bookings/confirmation/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/cancel/<str:booking_id>/', views.booking_cancel, name='booking_cancel'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notification/read/<str:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Feedback
    path('feedback/create/<str:booking_id>/', views.feedback_create, name='feedback_create'),
    
    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    
    # Maintenance
    path('maintenance/create/', views.maintenance_request_create, name='maintenance_request_create'),
    
    # Hall Management
    path('admin/halls/', views.admin_hall_list, name='admin_hall_list'),
    path('admin/halls/create/', views.hall_create, name='hall_create'),
    path('admin/halls/<uuid:hall_id>/update/', views.hall_update, name='hall_update'),
    path('admin/halls/<uuid:hall_id>/delete/', views.hall_delete, name='hall_delete'),
    path('admin/halls/<uuid:hall_id>/detail/', views.admin_hall_detail, name='admin_hall_detail'),
    
    # Amenity Management
    path('admin/amenities/', views.amenity_list, name='amenity_list'),
    path('admin/amenities/create/', views.amenity_create, name='amenity_create'),
    path('admin/amenities/<uuid:amenity_id>/update/', views.amenity_update, name='amenity_update'),
    path('admin/amenities/<uuid:amenity_id>/delete/', views.amenity_delete, name='amenity_delete'),
    

]