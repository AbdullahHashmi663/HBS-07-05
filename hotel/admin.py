from django.contrib import admin
from .models import RoomType, Room, Guest, Booking, UserProfile

class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_night', 'capacity', 'created_at')
    search_fields = ('name',)
    list_filter = ('capacity',)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'room_type', 'status', 'floor')
    list_filter = ('status', 'floor', 'room_type')
    search_fields = ('number',)

class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'id_number')
    list_filter = ('created_at',)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'guest', 'room', 'check_in_date', 'check_out_date', 'status', 'total_price', 'payment_status')
    list_filter = ('status', 'payment_status', 'check_in_date', 'check_out_date')
    search_fields = ('guest__full_name', 'room__number', 'booking_id')
    date_hierarchy = 'check_in_date'
    readonly_fields = ('booking_id', 'created_at', 'updated_at')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(Booking, BookingAdmin)
