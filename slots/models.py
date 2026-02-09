"""
Models for Cricket Slot Booking System
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime


class Venue(models.Model):
    """
    Represents a Cricket Venue with all amenities and policies
    """
    name = models.CharField(
        max_length=200,
        default="Box Cricket Turf",
        help_text="Name of the venue"
    )
    
    # Amenities
    has_seating = models.BooleanField(default=True, help_text="Seating area available")
    has_lighting = models.BooleanField(default=True, help_text="Lighting facility available")
    has_restrooms = models.BooleanField(default=True, help_text="Restrooms available")
    has_equipments = models.BooleanField(default=True, help_text="Cricket equipments available")
    has_parking = models.BooleanField(default=True, help_text="Parking facility available")
    
    # Number of turfs/boxes
    total_boxes = models.IntegerField(default=1, help_text="Total number of box-cricket turfs")
    
    # Pricing
    weekday_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=600.00,
        help_text="Price per hour on weekdays (Mon-Fri)"
    )
    weekend_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=700.00,
        help_text="Price per hour on weekends (Sat-Sun)"
    )
    advance_percentage = models.IntegerField(
        default=20,
        help_text="Advance amount percentage required for booking"
    )
    
    # Contact Information
    email = models.EmailField(
        default="vamsibilla248@gmail.com",
        help_text="Contact email"
    )
    phone = models.CharField(
        max_length=20,
        default="+91 7801019106",
        help_text="Contact phone number"
    )
    
    # Timing
    opening_time = models.TimeField(default="10:00:00", help_text="Opening time")
    closing_time = models.TimeField(default="18:00:00", help_text="Closing time")
    
    # Policies
    no_cancellation = models.BooleanField(
        default=True,
        help_text="No cancellation policy"
    )
    no_reschedule = models.BooleanField(
        default=True,
        help_text="No reschedule policy"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venue'
        verbose_name_plural = 'Venues'
    
    def __str__(self):
        return self.name
    
    @property
    def weekday_advance_amount(self):
        """Get advance amount for weekday booking"""
        return (self.weekday_price * self.advance_percentage) / 100
    
    @property
    def weekend_advance_amount(self):
        """Get advance amount for weekend booking"""
        return (self.weekend_price * self.advance_percentage) / 100


class Slot(models.Model):
    """
    Represents a Cricket Slot available for booking
    """
    CRICKET_TYPE_CHOICES = [
        ('box', 'Box Cricket'),
        ('normal', 'Normal Cricket'),
    ]
    
    TIME_SLOT_CHOICES = [
        ('6-7', '6:00 AM - 7:00 AM'),
        ('7-8', '7:00 AM - 8:00 AM'),
        ('8-9', '8:00 AM - 9:00 AM'),
        ('5-6', '5:00 PM - 6:00 PM'),
        ('6-7pm', '6:00 PM - 7:00 PM'),
        ('7-8pm', '7:00 PM - 8:00 PM'),
    ]
    
    date = models.DateField(help_text="Date of the cricket match")
    time_slot = models.CharField(
        max_length=10,
        choices=TIME_SLOT_CHOICES,
        help_text="Time slot for the match"
    )
    cricket_type = models.CharField(
        max_length=10,
        choices=CRICKET_TYPE_CHOICES,
        help_text="Type of cricket - Box or Normal"
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=500,
        help_text="Price per slot"
    )
    max_players = models.IntegerField(
        default=11,
        help_text="Maximum number of players"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('date', 'time_slot', 'cricket_type')
        ordering = ['date', 'time_slot']
        verbose_name = 'Cricket Slot'
        verbose_name_plural = 'Cricket Slots'
        
    def __str__(self):
        return f"{self.cricket_type.upper()} - {self.date} - {self.get_time_slot_display()}"
    
    @property
    def is_available(self):
        """Check if slot is available (not fully booked)"""
        booking_count = Booking.objects.filter(slot=self, status='confirmed').count()
        return booking_count < self.max_players
    
    @property
    def booked_count(self):
        """Get number of confirmed bookings"""
        return Booking.objects.filter(slot=self, status='confirmed').count()


class Booking(models.Model):
    """
    Represents a booking made by a user for a cricket slot
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'slot')  # Prevent double booking
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    
    def __str__(self):
        return f"{self.user.username} - {self.slot} - {self.status}"
    
    def clean(self):
        """Validate booking constraints"""
        # Check if slot is available
        if not self.slot.is_available and self.pk is None:
            raise ValidationError('This slot is no longer available.')
        
        # Check for duplicate booking
        existing_booking = Booking.objects.filter(
            user=self.user,
            slot=self.slot,
            status__in=['confirmed', 'pending']
        ).exclude(pk=self.pk)
        
        if existing_booking.exists():
            raise ValidationError('You have already booked this slot.')
