"""
Views for Cricket Slot Booking System
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from datetime import datetime, timedelta
from django.core.paginator import Paginator

from .models import Slot, Booking, Venue
from .forms import RegisterForm, BookingForm


def venue(request):
    """
    Venue information page - shows amenities, policies, pricing, and contact info
    """
    # Get the first venue or create default one
    venue_obj = Venue.objects.first()
    
    if not venue_obj:
        # Create a default venue if none exists
        venue_obj = Venue.objects.create()
    
    context = {
        'venue': venue_obj,
    }
    return render(request, 'slots/venue.html', context)


def dashboard(request):
    """
    Main Dashboard - Shows available slots (public for everyone) with pagination
    """
    today = datetime.now().date()
    
    # Get all slots (no limit, we'll paginate)
    all_slots = Slot.objects.filter(date__gte=today).order_by('date', 'time_slot')
    
    # Paginate slots - 6 per page
    paginator = Paginator(all_slots, 6)
    page_number = request.GET.get('page')
    slots_page = paginator.get_page(page_number)
    
    # Get venue info
    venue_obj = Venue.objects.first()
    
    # Get all available dates for filter
    available_dates = Slot.objects.filter(date__gte=today).values_list('date', flat=True).distinct().order_by('date')[:30]
    
    context = {
        'slots': slots_page,
        'available_dates': available_dates,
        'venue': venue_obj,
        'today': today,
    }
    return render(request, 'slots/dashboard.html', context)


def home(request):
    """
    Alias for dashboard - redirects to dashboard
    """
    return redirect('slots:dashboard')


@require_http_methods(["GET", "POST"])
def register(request):
    """
    User Registration View
    """
    # If already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('slots:dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Create new user
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1']
                )
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('slots:login')
            except IntegrityError:
                form.add_error('username', 'Username already exists!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'slots/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User Login View - redirects back to dashboard after login
    """
    # If already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('slots:dashboard')
    
    next_url = request.GET.get('next', 'slots:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! 🎉')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'slots/login.html', {'next': next_url})


@require_http_methods(["GET"])
def logout_view(request):
    """
    User Logout View
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('slots:dashboard')


@login_required
@require_http_methods(["GET"])
def my_dashboard(request):
    """
    User's personal dashboard - Shows their bookings
    """
    # Get user's bookings
    user_bookings = Booking.objects.filter(user=request.user).select_related('slot').order_by('-created_at')
    
    # Get upcoming confirmed bookings
    today = datetime.now().date()
    upcoming_bookings = user_bookings.filter(
        status='confirmed', 
        slot__date__gte=today
    ).order_by('slot__date', 'slot__time_slot')
    
    # Get past bookings
    past_bookings = user_bookings.filter(
        status='confirmed',
        slot__date__lt=today
    ).order_by('-slot__date')[:10]
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'total_bookings': user_bookings.count(),
    }
    
    return render(request, 'slots/my_dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def book_slot(request, slot_id):
    """
    Book a cricket slot
    """
    slot = get_object_or_404(Slot, id=slot_id)
    
    # Check if slot is available
    if not slot.is_available:
        messages.error(request, 'This slot is no longer available. All spots are booked.')
        return redirect('slots:dashboard')
    
    if request.method == 'POST':
        try:
            # Check for existing booking first
            existing_booking = Booking.objects.filter(
                user=request.user,
                slot=slot,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if existing_booking:
                messages.warning(
                    request,
                    f'⚠️ You have already booked this slot ({slot.get_cricket_type_display()} on {slot.date} {slot.get_time_slot_display()})'
                )
                return redirect('slots:dashboard')
            
            # Double-check slot availability before booking
            if not slot.is_available:
                messages.error(request, 'This slot is no longer available. Someone just booked the last spot!')
                return redirect('slots:dashboard')
            
            # Create booking with explicit field assignment
            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                status='confirmed'
            )
            
            messages.success(
                request,
                f'✅ Booking Confirmed! {slot.get_cricket_type_display()} on {slot.date} ({slot.get_time_slot_display()})'
            )
            return redirect('slots:my_bookings')
                
        except Exception as e:
            messages.error(request, f'Booking failed: {str(e)}')
            return redirect('slots:dashboard')
    
    # GET request - show booking confirmation page
    form = BookingForm()
    context = {
        'slot': slot,
        'form': form,
    }
    return render(request, 'slots/book_slot.html', context)


@login_required
@require_http_methods(["GET"])
def my_bookings(request):
    """
    Show user's bookings
    """
    bookings = Booking.objects.filter(user=request.user).select_related('slot').order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'slots/my_bookings.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    """
    Cancel a booking
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'confirmed':
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('slots:my_bookings')
    
    booking.status = 'cancelled'
    booking.save()
    
    messages.success(
        request,
        f'Booking cancelled successfully. ({booking.slot.get_cricket_type_display()} on {booking.slot.date})'
    )
    return redirect('slots:my_bookings')


@login_required
@require_http_methods(["GET"])
def booking_history(request):
    """
    Show user's complete booking history
    """
    bookings = Booking.objects.filter(user=request.user).select_related('slot').order_by('-created_at')
    
    # Separate by status
    confirmed_bookings = bookings.filter(status='confirmed')
    cancelled_bookings = bookings.filter(status='cancelled')
    
    context = {
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_bookings': bookings.count(),
    }
    return render(request, 'slots/booking_history.html', context)

