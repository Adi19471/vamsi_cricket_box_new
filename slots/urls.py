"""
URL Configuration for Slots App
"""
from django.urls import path
from . import views

app_name = 'slots'

urlpatterns = [
    # Main page - Dashboard (public, shows available slots)
    path('', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User pages (require login)
    path('my-dashboard/', views.my_dashboard, name='my_dashboard'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking-history/', views.booking_history, name='booking_history'),
    
    # Booking page (requires login)
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    
    # Venue info (public)
    path('venue/', views.venue, name='venue'),
]

