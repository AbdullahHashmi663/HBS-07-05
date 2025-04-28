import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from hotel.models import Guest, Room, RoomType, Booking

class Command(BaseCommand):
    help = 'Generate sample booking data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--bookings', type=int, default=20, help='Number of bookings to generate')
        parser.add_argument('--days', type=int, default=30, help='Number of past days to distribute bookings')

    def handle(self, *args, **options):
        num_bookings = options['bookings']
        days_range = options['days']
        
        # Check if we have rooms and guests
        if Room.objects.count() == 0:
            self.stdout.write(self.style.ERROR('No rooms found. Please create rooms first.'))
            return
            
        if Guest.objects.count() == 0:
            self.stdout.write(self.style.ERROR('No guests found. Please create guests first.'))
            return
            
        # Get admin user (or first user)
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
            
        # Get all rooms and guests
        rooms = list(Room.objects.all())
        guests = list(Guest.objects.all())
        
        # Get end date (today)
        end_date = timezone.now().date()
        
        # Calculate start date
        start_date = end_date - timedelta(days=days_range)
        
        # Generate bookings
        created_count = 0
        for _ in range(num_bookings):
            # Select random room and guest
            room = random.choice(rooms)
            guest = random.choice(guests)
            
            # Generate random check-in date (between start_date and end_date-1)
            checkin_offset = random.randint(0, days_range - 2)
            check_in_date = start_date + timedelta(days=checkin_offset)
            
            # Generate random stay duration (1-7 days)
            stay_duration = random.randint(1, 7)
            check_out_date = check_in_date + timedelta(days=stay_duration)
            
            # Ensure check_out_date is not in the future
            if check_out_date > end_date:
                check_out_date = end_date
            
            # Calculate price
            stay_nights = (check_out_date - check_in_date).days
            if stay_nights <= 0:
                continue  # Skip if dates don't make sense
                
            total_price = room.room_type.price_per_night * stay_nights
            
            # Determine status based on dates
            today = timezone.now().date()
            if check_out_date < today:
                status = 'checked_out'
            elif check_in_date <= today < check_out_date:
                status = 'checked_in'
            else:
                status = 'confirmed'
            
            # Check if there's a conflicting booking
            conflicts = Booking.objects.filter(
                room=room,
                check_out_date__gt=check_in_date,
                check_in_date__lt=check_out_date,
                status__in=['confirmed', 'checked_in']
            )
            
            if conflicts.exists():
                continue  # Skip if there's a conflict
            
            # Create booking
            try:
                Booking.objects.create(
                    guest=guest,
                    room=room,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    status=status,
                    adults=random.randint(1, 3),
                    children=random.randint(0, 2),
                    total_price=total_price,
                    payment_status=True,
                    special_requests="Sample generated booking",
                    created_by=admin_user,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 10))
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating booking: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} sample bookings')) 