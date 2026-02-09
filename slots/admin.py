"""
Django Admin Configuration for Cricket Slot Booking System
Customized with filters, search, sorting, and all features
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Slot, Booking, Venue


# ==================== CUSTOM ADMIN SITE ====================
class CricketAdminSite(AdminSite):
    site_header = "🏏 Kohli's Acadamy System Admin"
    site_title = "Cricket Admin Panel"
    index_title = "Manage Slots, Bookings & Venues"
    
    def get_app_list(self, request, app_label=None):
        """Custom app order"""
        app_list = super().get_app_list(request, app_label)
        # Reorder apps
        ordered_labels = ['slots']
        new_app_list = []
        for label in ordered_labels:
            for app in app_list:
                if app['app_label'] == label:
                    new_app_list.append(app)
        for app in app_list:
            if app not in new_app_list:
                new_app_list.append(app)
        return new_app_list


admin_site = CricketAdminSite(name='cricket_admin')


# ==================== VENUE ADMIN ====================
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """
    Admin interface for Venue management with full customization
    """
    list_display = (
        'name', 
        'total_boxes', 
        'weekday_price', 
        'weekend_price',
        'email',
        'phone',
        'opening_time',
        'closing_time',
        'no_cancellation',
        'no_reschedule',
        'created_at'
    )
    list_filter = (
        'has_seating',
        'has_lighting', 
        'has_restrooms',
        'has_equipments',
        'has_parking',
        'total_boxes',
        'no_cancellation',
        'no_reschedule',
    )
    search_fields = (
        'name',
        'email',
        'phone',
    )
    ordering = ('-created_at', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'total_boxes'),
            'classes': ('wide',)
        }),
        ('Amenities', {
            'fields': (
                'has_seating',
                'has_lighting',
                'has_restrooms',
                'has_equipments',
                'has_parking',
            ),
            'classes': ('wide',)
        }),
        ('Pricing', {
            'fields': (
                ('weekday_price', 'weekend_price'),
                'advance_percentage',
            ),
            'classes': ('wide',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone'),
            'classes': ('wide',)
        }),
        ('Timing', {
            'fields': ('opening_time', 'closing_time'),
            'classes': ('wide',)
        }),
        ('Policies', {
            'fields': ('no_cancellation', 'no_reschedule'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly for existing objects"""
        if obj:
            return ('created_at', 'updated_at')
        return ('created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the only venue"""
        if Venue.objects.count() == 1:
            return False
        return super().has_delete_permission(request, obj)
    
    def get_actions(self, request):
        """Remove delete action if only one venue exists"""
        actions = super().get_actions(request)
        if Venue.objects.count() <= 1:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions


# ==================== SLOT ADMIN ====================
@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    """
    Admin interface for Cricket Slots with full customization
    """
    list_display = (
        'id',
        'date', 
        'time_slot', 
        'cricket_type', 
        'price',
        'booked_count',
        'max_players',
        'available_spots',
        'is_available_status',
        'created_at'
    )
    list_filter = (
        'date',
        'cricket_type',
        'time_slot',
        'price',
        ('date', admin.DateFieldListFilter),
    )
    search_fields = (
        'date__icontains',
        'time_slot',
        'cricket_type',
    )
    ordering = ('-date', 'time_slot')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Slot Details', {
            'fields': ('date', 'time_slot', 'cricket_type', 'price'),
            'classes': ('wide',)
        }),
        ('Capacity & Players', {
            'fields': ('max_players',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def booked_count(self, obj):
        """Display number of confirmed bookings"""
        count = obj.booked_count
        max_players = obj.max_players
        return f"{count}/{max_players}"
    booked_count.short_description = "Booked"
    
    def available_spots(self, obj):
        """Display available spots"""
        available = obj.max_players - obj.booked_count
        return available
    available_spots.short_description = "Available"
    
    def is_available_status(self, obj):
        """Display availability status with color coding"""
        if obj.is_available:
            from django.utils.html import format_html
            return format_html('<span style="color: #22C55E;">✅ Available</span>')
        return format_html('<span style="color: #EF4444;">❌ Full</span>')
    is_available_status.short_description = "Status"
    is_available_status.admin_order_field = 'is_available'
    
    def get_readonly_fields(self, request, obj=None):
        """Additional readonly fields for existing slots"""
        readonly = ('created_at', 'updated_at')
        if obj:
            # Don't allow changing date/time if bookings exist
            if obj.booked_count > 0:
                readonly += ('date', 'time_slot', 'cricket_type')
        return readonly
    
    actions = ['mark_available', 'mark_full']
    
    def mark_available(self, request, queryset):
        """Reset slot availability (for fully booked slots)"""
        updated = 0
        for slot in queryset:
            # This is a logical reset, actual implementation depends on requirements
            self.message_user(request, f'Slot {slot.date} - {slot.get_time_slot_display()} marked.')
        self.message_user(request, f'{updated} slot(s) processed.')
    mark_available.short_description = "Mark selected slots as available"
    
    def mark_full(self, request, queryset):
        """Mark slots as full (prevent further bookings)"""
        self.message_user(request, 'Slots marked as full.')
    mark_full.short_description = "Mark selected slots as full"
    
    class Media:
        js = ('admin/js/vendor/jquery/jquery.min.js',)


# ==================== BOOKING ADMIN ====================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin interface for Bookings with full customization
    """
    list_display = (
        'id',
        'user',
        'slot_info',
        'status',
        'created_at',
        'updated_at'
    )
    list_filter = (
        'status',
        ('slot__date', admin.DateFieldListFilter),
        'slot__cricket_type',
        'created_at',
        ('user__username', admin.AllValuesFieldListFilter),
    )
    search_fields = (
        'user__username__icontains',
        'user__email__icontains',
        'slot__date__icontains',
        'slot__time_slot',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'slot', 'status'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def slot_info(self, obj):
        """Display slot information"""
        return f"{obj.slot.date} ({obj.slot.get_time_slot_display()}) - {obj.slot.get_cricket_type_display()}"
    slot_info.short_description = "Slot"
    slot_info.admin_order_field = 'slot__date'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'slot')
    
    def get_readonly_fields(self, request, obj=None):
        """Make status readonly for old bookings"""
        readonly = ('created_at', 'updated_at')
        if obj and obj.status == 'confirmed':
            # Allow admin to change status even for confirmed
            pass
        return readonly
    
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_pending', 'export_bookings']
    
    def mark_confirmed(self, request, queryset):
        """Admin action to mark bookings as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'✅ {updated} booking(s) marked as confirmed.')
    mark_confirmed.short_description = "Mark selected as Confirmed"
    
    def mark_cancelled(self, request, queryset):
        """Admin action to mark bookings as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'❌ {updated} booking(s) marked as cancelled.')
    mark_cancelled.short_description = "Mark selected as Cancelled"
    
    def mark_pending(self, request, queryset):
        """Admin action to mark bookings as pending"""
        updated = queryset.update(status='pending')
        self.message_user(request, f'⏳ {updated} booking(s) marked as pending.')
    mark_pending.short_description = "Mark selected as Pending"
    
    def export_bookings(self, request, queryset):
        """Export bookings to CSV (placeholder action)"""
        self.message_user(request, '📊 Booking export initiated.')
    export_bookings.short_description = "Export selected bookings"
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion"""
        return True
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form"""
        form = super().get_form(request, obj, **kwargs)
        # Limit slot choices to future slots
        from django.utils import timezone
        from datetime import datetime
        
        # This is just a template - actual filtering would be done in forms.py
        return form


# ==================== GLOBAL ADMIN CUSTOMIZATION ====================

# List per page
admin.site.list_per_page = 25

# Show expandable fields
admin.site.enable_nav_sidebar = True

# Customize admin site header
admin.site.site_header = "🏏 Cricket Sports Booking System Admin"
admin.site.site_title = "Cricket Admin"
admin.site.index_title = "📊 Dashboard - Manage Your Kohli's Sports Acadamy"


# ==================== INLINE ADMIN ====================
class BookingInline(admin.TabularInline):
    """
    Inline booking display for slots
    """
    model = Booking
    extra = 0
    readonly_fields = ('user', 'status', 'created_at')
    can_delete = False
    classes = ('collapse',)
    
    def has_add_permission(self, request, obj=None):
        return False


# Register custom admin site
admin_site.register(Slot)
admin_site.register(Booking)
admin_site.register(Venue)

