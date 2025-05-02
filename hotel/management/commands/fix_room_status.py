from django.core.management.base import BaseCommand
from hotel.models import Room, Booking

class Command(BaseCommand):
    help = 'Fix room status based on active bookings'

    def handle(self, *args, **options):
        # Get all rooms
        rooms = Room.objects.all()
        
        for room in rooms:
            # Check for active bookings
            active_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'checked_in']
            ).count()
            
            # If no active bookings, set room as available
            if active_bookings == 0 and room.status != 'available':
                old_status = room.status
                room.status = 'available'
                room.save(update_fields=['status'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Room {room.number} status updated from {old_status} to available'
                    )
                ) 