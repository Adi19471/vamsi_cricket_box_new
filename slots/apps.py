"""
App configuration for Slots app
"""
from django.apps import AppConfig


class SlotsConfig(AppConfig):
    """
    Configuration class for the Slots application
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'slots'
    verbose_name = 'Cricket Slot Booking'
