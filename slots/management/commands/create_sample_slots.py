"""
Management command to create sample cricket slots for testing
Usage: python manage.py create_sample_slots
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from slots.models import Slot


class Command(BaseCommand):
    help = 'Creates sample cricket slots for testing'

    def handle(self, *args, **options):
        """Create sample slots for the next 30 days"""
        
        # Clear existing slots (optional)
        # Slot.objects.all().delete()
        
        today = timezone.now().date()
        created_count = 0
        
        # Time slots and cricket types to create
        time_slots = ['6-7', '7-8', '8-9', '5-6', '6-7pm', '7-8pm']
        cricket_types = ['box', 'normal']
        
        # Create slots for next 30 days
        for day in range(1, 31):
            slot_date = today + timedelta(days=day)
            
            # Create 2 slots per day (one Box, one Normal) for each time
            for cricket_type in cricket_types:
                for time_slot in time_slots:
                    try:
                        slot = Slot.objects.get_or_create(
                            date=slot_date,
                            time_slot=time_slot,
                            cricket_type=cricket_type,
                            defaults={
                                'price': 500 if cricket_type == 'box' else 400,
                                'max_players': 6 if cricket_type == 'box' else 11,
                            }
                        )
                        if slot[1]:  # If created
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created slot: {slot_date} - {time_slot} - {cricket_type}'
                                )
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error creating slot: {str(e)}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {created_count} cricket slots!'
            )
        )
