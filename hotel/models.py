from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=1)
    amenities = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    )
    
    number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    floor = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True, help_text='Upload a room photo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Room {self.number} - {self.room_type.name}"

class Guest(models.Model):
    ID_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('cnic', 'CNIC'),
        ('driving_license', 'Driving License'),
    ]

    COUNTRY_CHOICES = [
        ('PK', 'Pakistan'),
        ('US', 'United States'),
        ('GB', 'United Kingdom'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('IN', 'India'),
        ('AE', 'United Arab Emirates'),
        ('SA', 'Saudi Arabia'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    id_type = models.CharField(max_length=50, choices=ID_TYPE_CHOICES)
    id_number = models.CharField(max_length=50)
    id_document = models.ImageField(upload_to='guest_ids/', blank=True, null=True, help_text='Upload ID document (CNIC/Passport)')
    vehicle_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class Booking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    special_requests = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.guest.full_name}"

    def save(self, *args, **kwargs):
        # Calculate total price if not provided
        if not self.total_price:
            nights = (self.check_out_date - self.check_in_date).days
            self.total_price = self.room.room_type.price_per_night * nights
            
        # Update room status when booking is created or updated
        if self.status == 'confirmed':
            self.room.status = 'occupied'
            # Automatically set payment_status to True when status is 'confirmed'
            self.payment_status = True
        elif self.status == 'checked_in':
            self.room.status = 'occupied'
            # Ensure payment_status is True when checked in
            self.payment_status = True
        elif self.status in ['checked_out', 'cancelled', 'no_show']:
            self.room.status = 'available'
        
        self.room.save()
        super().save(*args, **kwargs)

class ThemeSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='theme_settings')
    primary_color = models.CharField(max_length=20, default='#4285F4')
    secondary_color = models.CharField(max_length=20, default='#34A853')
    danger_color = models.CharField(max_length=20, default='#EA4335')
    warning_color = models.CharField(max_length=20, default='#FBBC05')
    sidebar_color = models.CharField(max_length=20, default='#343a40')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Theme Settings for {self.user.username}"
