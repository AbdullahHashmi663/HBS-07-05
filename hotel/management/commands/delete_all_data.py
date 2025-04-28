from django.core.management.base import BaseCommand
from hotel.models import Booking, Room, RoomType

class Command(BaseCommand):
    help = 'Delete all records from rooms, room types, and bookings'

    def handle(self, *args, **options):
        # First delete all bookings
        booking_count = Booking.objects.count()
        Booking.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {booking_count} bookings'))

        # Then delete all rooms
        room_count = Room.objects.count()
        Room.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {room_count} rooms'))

        # Finally delete all room types
        room_type_count = RoomType.objects.count()
        RoomType.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {room_type_count} room types'))

        self.stdout.write(self.style.SUCCESS('All data has been successfully deleted')) 