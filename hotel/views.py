from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Avg, Sum, Count
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, RoomType, Guest, Booking, UserProfile, ThemeSettings, HotelInfo
from django.contrib.auth.models import User
from functools import wraps
from .forms import GuestForm, UserForm, RoomForm, ThemeSettingsForm, HotelInfoForm

from xhtml2pdf import pisa
import xlsxwriter
from io import BytesIO
import calendar

# Custom decorators for role-based permissions
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    return _wrapped_view

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'hotel/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard Views
@login_required
def dashboard(request):
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    active_bookings = Booking.objects.filter(
        Q(status='confirmed') | Q(status='checked_in')
    ).count()
    total_guests = Guest.objects.count()
    
    # For admin, show all bookings. For staff, show only active bookings
    if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
        recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    else:
        recent_bookings = Booking.objects.filter(
            Q(status='confirmed') | Q(status='checked_in')
        ).order_by('-created_at')[:5]
    
    # Get hotel info from database
    hotel_info = HotelInfo.get_default()
    
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'active_bookings': active_bookings,
        'total_guests': total_guests,
        'recent_bookings': recent_bookings,
        'user_role': request.user.profile.role if hasattr(request.user, 'profile') else None,
        'hotel_info': hotel_info
    }
    
    return render(request, 'hotel/dashboard.html', context)

# Room Types Views
@login_required
@admin_required
def room_type_list(request):
    room_types = RoomType.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        room_types = room_types.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(amenities__icontains=search_query)
        )
    
    # Handle capacity filter
    capacity_filter = request.GET.get('capacity')
    if capacity_filter:
        room_types = room_types.filter(capacity=capacity_filter)
    
    # Handle price range filter
    price_range = request.GET.get('price_range')
    if price_range:
        if price_range == 'budget':
            room_types = room_types.filter(price_per_night__lte=1000)
        elif price_range == 'standard':
            room_types = room_types.filter(price_per_night__gt=1000, price_per_night__lt=3000)
        elif price_range == 'luxury':
            room_types = room_types.filter(price_per_night__gte=3000)
    
    # Calculate statistics
    avg_price = room_types.aggregate(Avg('price_per_night'))['price_per_night__avg']
    total_capacity = room_types.aggregate(Sum('capacity'))['capacity__sum'] or 0
    
    # Get most popular room type (could be based on bookings if you have that relationship)
    # This is a placeholder - update based on your actual model relationships
    most_popular = room_types.first().name if room_types.exists() else "N/A"
    
    context = {
        'room_types': room_types,
        'avg_price': avg_price,
        'total_capacity': total_capacity,
        'most_popular': most_popular,
        'search_query': search_query,
        'capacity_filter': capacity_filter,
        'price_range': price_range
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the table content for AJAX requests
        return render(request, 'hotel/includes/room_type_table.html', context)
    
    return render(request, 'hotel/room_type_list.html', context)

@login_required
@admin_required
def room_type_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price_per_night = request.POST.get('price_per_night')
        capacity = request.POST.get('capacity')
        amenities = request.POST.get('amenities')
        
        RoomType.objects.create(
            name=name,
            description=description,
            price_per_night=price_per_night,
            capacity=capacity,
            amenities=amenities
        )
        
        messages.success(request, 'Room type created successfully')
        return redirect('room_type_list')
        
    return render(request, 'hotel/room_type_form.html')

@login_required
@admin_required
def room_type_edit(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    
    if request.method == 'POST':
        room_type.name = request.POST.get('name')
        room_type.description = request.POST.get('description')
        room_type.price_per_night = request.POST.get('price_per_night')
        room_type.capacity = request.POST.get('capacity')
        room_type.amenities = request.POST.get('amenities')
        room_type.save()
        
        messages.success(request, 'Room type updated successfully')
        return redirect('room_type_list')
        
    return render(request, 'hotel/room_type_form.html', {'room_type': room_type})

@login_required
@admin_required
def room_type_delete(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    
    if request.method == 'POST':
        room_type.delete()
        messages.success(request, 'Room type deleted successfully')
        return redirect('room_type_list')
        
    return render(request, 'hotel/room_type_delete.html', {'room_type': room_type})

# Room Views
@login_required
def room_list(request):
    rooms = Room.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        rooms = rooms.filter(
            Q(number__icontains=search_query) |
            Q(room_type__name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Handle room type filter
    type_filter = request.GET.get('type')
    if type_filter:
        rooms = rooms.filter(room_type_id=type_filter)
    
    # Handle status filter
    status_filter = request.GET.get('status')
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    
    # Handle floor filter
    floor_filter = request.GET.get('floor')
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)
    
    # Get all room types for filter dropdown
    room_types = RoomType.objects.all()
    
    # Get distinct floors for filter dropdown
    floors = Room.objects.values_list('floor', flat=True).distinct().order_by('floor')
    
    # Calculate statistics
    context = {
        'rooms': rooms,
        'room_types': room_types,
        'floors': floors,
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(status='available').count(),
        'occupied_rooms': Room.objects.filter(status='occupied').count(),
        'maintenance_rooms': Room.objects.filter(status='maintenance').count(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the table content for AJAX requests
        return render(request, 'hotel/includes/room_table.html', context)
    
    return render(request, 'hotel/room_list.html', context)

@login_required
@admin_required
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            messages.success(request, 'Room created successfully')
            return redirect('room_list')
    else:
        form = RoomForm()
        
    return render(request, 'hotel/room_form.html', {'form': form})

@login_required
@admin_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    
    # Check if room has active bookings
    active_bookings = Booking.objects.filter(
        room=room,
        status__in=['confirmed', 'checked_in']
    ).count()
    
    if active_bookings > 0:
        messages.error(request, f'Cannot edit room {room.number} as it has active bookings. Please wait until all bookings are completed.')
        return redirect('room_list')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, 'Room updated successfully')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
        
    return render(request, 'hotel/room_form.html', {'form': form, 'room': room})

@login_required
@admin_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    
    # Check if there are any active bookings for this room
    active_bookings = Booking.objects.filter(
        room=room,
        status__in=['confirmed', 'checked_in']
    ).count()
    
    if request.method == 'POST':
        try:
            # If force delete parameter is passed, delete anyway
            if request.POST.get('force_delete'):
                room.delete()
                messages.success(request, f'Room {room.number} has been deleted successfully.')
                return redirect('room_list')
            
            # Otherwise, check if there are active bookings
            if active_bookings > 0:
                messages.error(request, f'Cannot delete room {room.number} as it has {active_bookings} active booking(s). Cancel the bookings first or use force delete.')
                return render(request, 'hotel/room_delete.html', {
                    'room': room,
                    'active_bookings': active_bookings
                })
                
            # No active bookings, proceed with deletion
            room.delete()
            messages.success(request, f'Room {room.number} has been deleted successfully.')
            return redirect('room_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting room: {str(e)}')
    
    return render(request, 'hotel/room_delete.html', {
        'room': room,
        'active_bookings': active_bookings
    })

@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    bookings = Booking.objects.filter(room=room).order_by('-check_in_date')[:5]
    return render(request, 'hotel/room_detail.html', {'room': room, 'bookings': bookings})

# Guest Views
@login_required
def guest_list(request):
    guests = Guest.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        guests = guests.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Handle country filter
    country_filter = request.GET.get('country')
    if country_filter:
        guests = guests.filter(country=country_filter)
    
    # Handle guest type filter
    guest_type_filter = request.GET.get('type')
    if guest_type_filter == 'corporate':
        # Implement your logic for corporate guests
        # This is a placeholder, adjust based on your actual model
        guests = guests.filter(notes__icontains='corporate')
    elif guest_type_filter == 'individual':
        # Implement your logic for individual guests
        # This is a placeholder, adjust based on your actual model
        guests = guests.exclude(notes__icontains='corporate')
    
    # Prepare country choices for filter dropdown
    countries = Guest.COUNTRY_CHOICES
    
    # Calculate statistics
    total_guests = guests.count()
    corporate_guests = Guest.objects.filter(notes__icontains='corporate').count()  # Placeholder logic
    
    # Guests with more than one booking
    returning_guests = 0
    for guest in Guest.objects.all():
        if guest.bookings.count() > 1:
            returning_guests += 1
    
    # New guests in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_guests = Guest.objects.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'guests': guests,
        'countries': countries,
        'total_guests': total_guests,
        'corporate_guests': corporate_guests,
        'returning_guests': returning_guests,
        'new_guests': new_guests,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the table content for AJAX requests
        return render(request, 'hotel/guest_table.html', context)
    
    return render(request, 'hotel/guest_list.html', context)

@login_required
def guest_create(request):
    if request.method == 'POST':
        form = GuestForm(request.POST, request.FILES)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest {guest.full_name} created successfully')
            
            # Check if there's a redirect parameter from booking form
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            
            return redirect('guest_list')
    else:
        form = GuestForm()
        # Pass the next parameter to the form if provided
        next_url = request.GET.get('next')
        
    return render(request, 'hotel/guest_form.html', {'form': form, 'next_url': next_url if 'next_url' in locals() else None})

@login_required
def guest_edit(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    
    if request.method == 'POST':
        form = GuestForm(request.POST, request.FILES, instance=guest)
        if form.is_valid():
            guest_form = form.save(commit=False)
            # Keep the existing ID document if no new one is uploaded
            if not request.FILES.get('id_document') and guest.id_document:
                guest_form.id_document = guest.id_document
            guest_form.save()
            messages.success(request, 'Guest updated successfully')
            return redirect('guest_list')
    else:
        form = GuestForm(instance=guest)
        
    return render(request, 'hotel/guest_form.html', {'form': form, 'guest': guest})

@login_required
def guest_delete(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    
    # Check if there are any active bookings for this guest
    active_bookings = Booking.objects.filter(
        guest=guest,
        status__in=['confirmed', 'checked_in']
    ).count()
    
    # Get total bookings and revenue for this guest
    total_bookings = Booking.objects.filter(guest=guest).count()
    total_spent = Booking.objects.filter(guest=guest).aggregate(total=Sum('total_price'))['total'] or 0
    
    if request.method == 'POST':
        try:
            # If force delete parameter is passed, delete anyway
            if request.POST.get('force_delete') or active_bookings == 0:
                # Guest deletion will cascade to bookings due to ForeignKey relationship
                guest.delete()
                messages.success(request, f'Guest {guest.full_name} has been deleted successfully along with all associated bookings.')
                return redirect('guest_list')
            
            # Otherwise, show a warning about active bookings
            messages.error(request, f'Cannot delete guest {guest.full_name} as they have {active_bookings} active booking(s). Cancel the bookings first or use force delete.')
            return render(request, 'hotel/guest_delete.html', {
                'guest': guest,
                'active_bookings': active_bookings,
                'total_bookings': total_bookings,
                'total_spent': total_spent
            })
            
        except Exception as e:
            messages.error(request, f'Error deleting guest: {str(e)}')
    
    return render(request, 'hotel/guest_delete.html', {
        'guest': guest,
        'active_bookings': active_bookings,
        'total_bookings': total_bookings,
        'total_spent': total_spent
    })

@login_required
def guest_detail(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    bookings = Booking.objects.filter(guest=guest).order_by('-check_in_date')
    
    # Calculate statistics
    total_nights = 0
    total_spent = 0
    last_visit = None
    
    for booking in bookings:
        if booking.check_in_date and booking.check_out_date:
            nights = (booking.check_out_date - booking.check_in_date).days
            total_nights += nights
            total_spent += booking.total_price
            
            # Track last visit
            if not last_visit or booking.check_in_date > last_visit:
                last_visit = booking.check_in_date
    
    context = {
        'guest': guest,
        'bookings': bookings,
        'total_nights': total_nights,
        'total_spent': total_spent,
        'last_visit': last_visit
    }
    
    return render(request, 'hotel/guest_detail.html', context)

# Booking Views
@login_required
def booking_list(request):
    # For admin, show all bookings. For staff, show only active bookings
    if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
        bookings = Booking.objects.all().order_by('-created_at')
    else:
        bookings = Booking.objects.filter(
            Q(status='confirmed') | Q(status='checked_in')
        ).order_by('-created_at')
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        bookings = bookings.filter(
            Q(guest__full_name__icontains=search_query) |
            Q(booking_id__icontains=search_query) |
            Q(room__number__icontains=search_query)
        )
    
    # Handle status filter
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Handle date filter
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings = bookings.filter(
                Q(check_in_date=filter_date) | 
                Q(check_out_date=filter_date)
            )
        except ValueError:
            # Invalid date format, ignore filter
            pass
    
    # Handle room type filter
    room_type_filter = request.GET.get('room_type')
    if room_type_filter:
        bookings = bookings.filter(room__room_type_id=room_type_filter)
    
    # Get room types for filter dropdown
    room_types = RoomType.objects.all()
    
    # Calculate statistics
    today = timezone.now().date()
    context = {
        'bookings': bookings,
        'room_types': room_types,
        'total_bookings': Booking.objects.count(),
        'active_bookings': Booking.objects.filter(Q(status='confirmed') | Q(status='checked_in')).count(),
        'todays_checkins': Booking.objects.filter(check_in_date=today).count(),
        'todays_checkouts': Booking.objects.filter(check_out_date=today).count(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the table content for AJAX requests
        return render(request, 'hotel/includes/booking_table.html', context)
    
    return render(request, 'hotel/booking_list.html', context)

@login_required
@admin_required
def booking_create(request):
    guests = Guest.objects.all()
    available_rooms = Room.objects.filter(status='available')
    
    if request.method == 'POST':
        guest_id = request.POST.get('guest')
        room_id = request.POST.get('room')
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        
        # Basic validation
        if not all([guest_id, room_id, check_in_date, check_out_date]):
            messages.error(request, 'All fields are required')
            return render(request, 'hotel/booking_form.html', {
                'guests': guests,
                'rooms': available_rooms
            })
        
        try:
            guest = Guest.objects.get(pk=guest_id)
            room = Room.objects.get(pk=room_id)
            
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
            
            # Ensure check_out is after check_in
            if check_out <= check_in:
                messages.error(request, 'Check-out date must be after check-in date')
                return render(request, 'hotel/booking_form.html', {
                    'guests': guests,
                    'rooms': available_rooms
                })
                
            # Check if room is available for these dates
            conflicts = Booking.objects.filter(
                room=room,
                check_out_date__gt=check_in,
                check_in_date__lt=check_out,
                status__in=['confirmed', 'checked_in']
            )
            
            if conflicts.exists():
                messages.error(request, f'Room {room.number} is not available for the selected dates')
                return render(request, 'hotel/booking_form.html', {
                    'guests': guests,
                    'rooms': available_rooms
                })
            
            # Calculate total price
            nights = (check_out - check_in).days
            total_price = room.room_type.price_per_night * nights
            
            # Create booking
            booking = Booking(
                guest=guest,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
                status='confirmed',  # Default to confirmed
                payment_status=True if request.POST.get('payment_status') == 'on' else False,  # Set payment status based on form input
                adults=request.POST.get('adults', 1),
                children=request.POST.get('children', 0),
                total_price=total_price,
                special_requests=request.POST.get('special_requests', ''),
                created_by=request.user
            )
            booking.save()
            
            messages.success(request, 'Booking created successfully')
            return redirect('booking_detail', pk=booking.pk)
            
        except (Guest.DoesNotExist, Room.DoesNotExist):
            messages.error(request, 'Invalid guest or room selected')
        except ValueError:
            messages.error(request, 'Invalid date format')
    
    return render(request, 'hotel/booking_form.html', {
        'guests': guests,
        'rooms': available_rooms
    })

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'hotel/booking_detail.html', {'booking': booking})

@login_required
@admin_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    guests = Guest.objects.all()
    
    # Include the current room in the list, even if it's not available
    available_rooms = list(Room.objects.filter(status='available'))
    if booking.room not in available_rooms:
        available_rooms.append(booking.room)
    
    if request.method == 'POST':
        booking.guest = get_object_or_404(Guest, pk=request.POST.get('guest'))
        booking.room = get_object_or_404(Room, pk=request.POST.get('room'))
        booking.check_in_date = request.POST.get('check_in_date')
        booking.check_out_date = request.POST.get('check_out_date')
        booking.status = request.POST.get('status')
        booking.adults = request.POST.get('adults', 1)
        booking.children = request.POST.get('children', 0)
        booking.payment_status = True if request.POST.get('payment_status') == 'on' else False
        booking.special_requests = request.POST.get('special_requests', '')
        
        # Recalculate total price
        check_in = datetime.strptime(booking.check_in_date, '%Y-%m-%d').date() if isinstance(booking.check_in_date, str) else booking.check_in_date
        check_out = datetime.strptime(booking.check_out_date, '%Y-%m-%d').date() if isinstance(booking.check_out_date, str) else booking.check_out_date
        nights = (check_out - check_in).days
        booking.total_price = booking.room.room_type.price_per_night * nights
        
        booking.save()
        
        messages.success(request, 'Booking updated successfully')
        return redirect('booking_detail', pk=booking.pk)
        
    return render(request, 'hotel/booking_form.html', {
        'booking': booking,
        'guests': guests,
        'rooms': available_rooms
    })

@login_required
@admin_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    room = booking.room
    
    if request.method == 'POST':
        try:
            # Store room info for updating later
            room_id = room.id
            
            # Delete the booking
            booking.delete()
            
            # Fetch fresh room instance and force update its status
            room = Room.objects.get(id=room_id)
            
            # Check if room has any other active bookings
            active_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'checked_in']
            ).count()
            
            if active_bookings == 0:
                room.status = 'available'
                room.save(update_fields=['status'])
                messages.success(request, f'Booking deleted and room {room.number} status updated to available')
            else:
                messages.info(request, f'Booking deleted but room {room.number} has other active bookings')
            
            return redirect('booking_list')
            
        except Exception as e:
            messages.error(request, f'Error during deletion: {str(e)}')
            return redirect('booking_list')
        
    return render(request, 'hotel/booking_delete.html', {'booking': booking})

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    room = booking.room
    
    if request.method == 'POST':
        try:
            # Update booking status to cancelled
            booking.status = 'cancelled'
            
            # Only set payment_status to False if it was unpaid to begin with
            # For paid bookings, we keep payment_status=True so they're counted in revenue
            if not booking.payment_status:
                booking.payment_status = False
                
            booking.save()
            
            # Check if room has any other active bookings
            active_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'checked_in']
            ).exclude(id=booking.id).count()
            
            if active_bookings == 0:
                room.status = 'available'
                room.save(update_fields=['status'])
                messages.success(request, f'Booking cancelled and room {room.number} status updated to available')
            else:
                messages.info(request, f'Booking cancelled but room {room.number} has other active bookings')
            
            return redirect('booking_list')
            
        except Exception as e:
            messages.error(request, f'Error during cancellation: {str(e)}')
            return redirect('booking_list')
        
    return render(request, 'hotel/booking_cancel.html', {'booking': booking})

@login_required
def check_room_availability(request):
    if request.method == 'GET':
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        
        if not check_in or not check_out:
            return JsonResponse({'error': 'Both check-in and check-out dates are required'}, status=400)
        
        # Convert string dates to date objects
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        # Find all bookings that overlap with the requested dates
        overlapping_bookings = Booking.objects.filter(
            Q(check_in_date__lt=check_out_date) & Q(check_out_date__gt=check_in_date)
        )
        
        # Get the rooms that are booked during this period
        booked_room_ids = overlapping_bookings.values_list('room_id', flat=True)
        
        # Find available rooms (not in booked_room_ids and not under maintenance)
        available_rooms = Room.objects.filter(status='available').exclude(id__in=booked_room_ids)
        
        # Format rooms for JSON response
        rooms_data = [{
            'id': room.id,
            'number': room.number,
            'type': room.room_type.name,
            'price': float(room.room_type.price_per_night),
            'capacity': room.room_type.capacity
        } for room in available_rooms]
        
        return JsonResponse({'available_rooms': rooms_data})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# User Management (for Admin only)
@login_required
@admin_required
def user_list(request):
    users = User.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Handle role filter
    role = request.GET.get('role')
    if role:
        if role == 'admin':
            users = users.filter(is_superuser=True)
        elif role == 'receptionist':
            users = users.filter(is_staff=False, is_superuser=False)
    
    # Handle status filter
    status = request.GET.get('status')
    if status:
        users = users.filter(is_active=(status == 'active'))
    
    # Calculate statistics
    context = {
        'users': users,
        'admin_count': User.objects.filter(is_superuser=True).count(),
        'receptionist_count': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'active_count': User.objects.filter(is_active=True).count(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the table content for AJAX requests
        return render(request, 'hotel/includes/user_table.html', context)
    
    return render(request, 'hotel/user_list.html', context)

@login_required
@admin_required
def user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    
    # Get user's bookings if they created any
    bookings_created = Booking.objects.filter(created_by=user_obj).order_by('-created_at')[:5]
    
    context = {
        'user_obj': user_obj,
        'bookings_created': bookings_created
    }
    
    return render(request, 'hotel/user_detail.html', context)

@login_required
def user_create(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to create users.')
        return redirect('user_list')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} was created successfully.')
            return redirect('user_list')
    else:
        form = UserForm()

    return render(request, 'hotel/user_form.html', {
        'form': form,
        'title': 'Create New User'
    })

@login_required
def user_edit(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit users.')
        return redirect('user_list')

    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user, is_edit=True)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} was updated successfully.')
            return redirect('user_list')
    else:
        initial_data = {
            'role': user.profile.role,
            'phone': user.profile.phone,
            'address': user.profile.address,
        }
        form = UserForm(instance=user, initial=initial_data, is_edit=True)

    return render(request, 'hotel/user_form.html', {
        'form': form,
        'user_obj': user,
        'title': f'Edit User: {user.username}'
    })

@login_required
@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('user_list')
        
    return render(request, 'hotel/user_delete.html', {'user_obj': user})

@login_required
@admin_required
def user_activate(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been activated')
    return redirect('user_list')

@login_required
@admin_required
def user_deactivate(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.username} has been deactivated')
    return redirect('user_list')

# Reports Views
@login_required
@admin_required
def reports(request):
    # Get data for reports dashboard
    total_bookings = Booking.objects.count()
    total_guests = Guest.objects.count()
    total_revenue = Booking.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Recent bookings
    recent_bookings = Booking.objects.order_by('-created_at')[:5]
    
    # Generate monthly revenue data for chart
    current_year = timezone.now().year
    monthly_revenue = []
    monthly_bookings = []
    
    for month in range(1, 13):
        bookings = Booking.objects.filter(
            created_at__year=current_year,
            created_at__month=month
        )
        revenue = bookings.aggregate(total=Sum('total_price'))['total'] or 0
        monthly_revenue.append(revenue)
        monthly_bookings.append(bookings.count())
    
    # Top room types by bookings
    room_types = RoomType.objects.all()
    room_type_bookings = []
    
    for room_type in room_types:
        booking_count = Booking.objects.filter(room__room_type=room_type).count()
        if booking_count > 0:
            room_type_bookings.append({
                'name': room_type.name,
                'count': booking_count
            })
    
    # Sort by booking count
    room_type_bookings.sort(key=lambda x: x['count'], reverse=True)
    
    # Get top 5 countries for guests
    guest_countries = {}
    for choice in Guest.COUNTRY_CHOICES:
        code, name = choice
        count = Guest.objects.filter(country=code).count()
        if count > 0:
            guest_countries[name] = count
    
    # Get top 5 countries sorted by count
    top_countries = sorted(guest_countries.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context = {
        'total_bookings': total_bookings,
        'total_guests': total_guests,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'monthly_revenue': monthly_revenue,
        'monthly_bookings': monthly_bookings,
        'room_type_bookings': room_type_bookings,
        'top_countries': top_countries,
    }
    
    return render(request, 'hotel/reports.html', context)

@login_required
def occupancy_report(request):
    # Time range filter
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    
    if start_date and end_date_param:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Using default 30-day range.')
            start_date = end_date - timedelta(days=30)
    else:
        # Default to last 30 days
        start_date = end_date - timedelta(days=30)
    
    # Calculate date range in days
    date_range = (end_date - start_date).days + 1  # +1 to include both start and end dates
    
    # Get all rooms
    rooms = Room.objects.all()
    total_rooms = rooms.count()
    
    # Get room types
    room_types = RoomType.objects.all()
    
    # Calculate overall occupancy rate
    total_possible_room_nights = total_rooms * date_range
    
    # Calculate occupied room nights from bookings
    occupied_room_nights = 0
    bookings = Booking.objects.filter(
        check_in_date__lte=end_date,
        check_out_date__gte=start_date,
        status__in=['confirmed', 'checked_in', 'checked_out']
    )
    
    for booking in bookings:
        # Calculate overlap between booking and the date range
        booking_start = max(booking.check_in_date, start_date)
        booking_end = min(booking.check_out_date, end_date)
        nights = (booking_end - booking_start).days + 1  # +1 to include both start and end dates
        occupied_room_nights += nights
    
    occupancy_percentage = (occupied_room_nights / total_possible_room_nights * 100) if total_possible_room_nights > 0 else 0
    
    # Calculate occupancy by room type
    room_type_occupancy = []
    for room_type in room_types:
        room_count = rooms.filter(room_type=room_type).count()
        type_room_nights = room_count * date_range
        
        if type_room_nights == 0:
            continue
            
        room_ids = rooms.filter(room_type=room_type).values_list('id', flat=True)
        type_occupied_nights = 0
        
        # Calculate type occupied nights from bookings
        for booking in bookings.filter(room__room_type=room_type):
            booking_start = max(booking.check_in_date, start_date)
            booking_end = min(booking.check_out_date, end_date)
            nights = (booking_end - booking_start).days + 1
            type_occupied_nights += nights
        
        occupancy_rate = (type_occupied_nights / type_room_nights) * 100 if type_room_nights > 0 else 0
        room_type_occupancy.append({
            'name': room_type.name,
            'occupancy_rate': round(occupancy_rate, 2),
            'room_count': room_count,
            'occupied_nights': type_occupied_nights,
            'total_nights': type_room_nights
        })
    
    # Calculate daily occupancy for chart - ensure each day in the range has data
    daily_occupancy = []
    
    # Create a dictionary to track occupied rooms by date
    occupied_by_date = {}
    
    # Loop through all bookings and count occupied rooms for each date
    for current_date in (start_date + timedelta(days=n) for n in range(date_range)):
        # Find bookings active on this date (including check-out day)
        day_occupied_count = bookings.filter(
            check_in_date__lte=current_date,
            check_out_date__gte=current_date
        ).count()
        
        # Calculate occupancy rate for this day
        day_occupancy_rate = (day_occupied_count / total_rooms) * 100 if total_rooms > 0 else 0
        
        # Add to our result array
        daily_occupancy.append({
            'date': current_date,
            'occupancy_rate': round(day_occupancy_rate, 2),
            'occupied_rooms': day_occupied_count,
            'total_rooms': total_rooms
        })
    
    # Sort daily_occupancy by date to ensure proper order
    daily_occupancy.sort(key=lambda x: x['date'])
    
    context = {
        'occupancy_percentage': round(occupancy_percentage, 2),
        'occupied_room_nights': occupied_room_nights,
        'total_possible_room_nights': total_possible_room_nights,
        'room_type_occupancy': room_type_occupancy,
        'daily_occupancy': daily_occupancy,
        'start_date': start_date,
        'end_date': end_date,
        'total_rooms': total_rooms
    }
    
    return render(request, 'hotel/occupancy_report.html', context)

@login_required
def revenue_report(request):
    # Time range filter (default to current year)
    end_date = timezone.now().date()
    current_year = end_date.year
    start_date = timezone.datetime(current_year, 1, 1).date()
    
    # Filter by year if provided
    selected_year = request.GET.get('year', str(current_year))
    selected_month = None
    try:
        selected_year = int(selected_year)
        start_date = timezone.datetime(selected_year, 1, 1).date()
        end_date = timezone.datetime(selected_year, 12, 31).date()
        
        # Month filter
        month = request.GET.get('month')
        if month:
            selected_month = int(month)
            # Set the date range to the selected month
            start_date = timezone.datetime(selected_year, selected_month, 1).date()
            
            # Calculate the last day of the month
            if selected_month == 12:
                end_date = timezone.datetime(selected_year, 12, 31).date()
            else:
                end_date = timezone.datetime(selected_year, selected_month + 1, 1).date() - timedelta(days=1)
    except (ValueError, TypeError):
        selected_year = current_year
        messages.error(request, 'Invalid year or month provided. Using current year instead.')
    
    # Get all bookings for display
    all_bookings = Booking.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    # Get revenue-generating bookings:
    # 1. Active bookings (not cancelled)
    # 2. Cancelled bookings that were paid
    revenue_bookings = Booking.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).filter(
        Q(~Q(status='cancelled')) | Q(status='cancelled', payment_status=True)
    )
    
    # Calculate total revenue from revenue-generating bookings
    total_revenue = revenue_bookings.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Calculate revenue by room type (including cancelled but paid bookings)
    revenue_by_room_type = {}
    revenue_percentages = {}
    
    for room_type in RoomType.objects.all():
        rt_bookings = revenue_bookings.filter(room__room_type=room_type)
        revenue = rt_bookings.aggregate(total=Sum('total_price'))['total'] or 0
        if revenue > 0:  # Only include room types with revenue
            revenue_by_room_type[room_type.name] = revenue
            revenue_percentages[room_type.name] = (revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    # Calculate days in period for average daily revenue
    days_in_period = (end_date - start_date).days + 1
    avg_daily_revenue = total_revenue / days_in_period if days_in_period > 0 else 0
    
    # Calculate monthly revenue (including cancelled but paid bookings)
    monthly_revenue = []
    for month in range(1, 13):
        month_bookings = revenue_bookings.filter(created_at__month=month)
        revenue = month_bookings.aggregate(total=Sum('total_price'))['total'] or 0
        booking_count = month_bookings.count()
        month_name = timezone.datetime(2000, month, 1).strftime('%B')
        
        monthly_revenue.append({
            'month': month_name,
            'revenue': revenue,
            'booking_count': booking_count
        })
    
    # Calculate available years for the dropdown
    available_years = Booking.objects.dates('created_at', 'year')
    years = [date.year for date in available_years]
    
    # Calculate statistics
    active_booking_count = all_bookings.exclude(status='cancelled').count()
    cancelled_paid_count = all_bookings.filter(status='cancelled', payment_status=True).count()
    cancelled_unpaid_count = all_bookings.filter(status='cancelled', payment_status=False).count()
    total_revenue_bookings = revenue_bookings.count()
    
    # Handle export requests
    export_format = request.GET.get('export')
    if export_format:
        if export_format == 'pdf':
            return generate_revenue_pdf(request, all_bookings, start_date, end_date, total_revenue, revenue_by_room_type, monthly_revenue)
        elif export_format == 'excel':
            return generate_revenue_excel(request, all_bookings, start_date, end_date, total_revenue, revenue_by_room_type, monthly_revenue)
    
    context = {
        'total_revenue': total_revenue,
        'revenue_by_room_type': revenue_by_room_type,
        'revenue_percentages': revenue_percentages,
        'monthly_revenue': monthly_revenue,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'available_years': years,
        'active_booking_count': active_booking_count,
        'cancelled_paid_count': cancelled_paid_count,
        'cancelled_unpaid_count': cancelled_unpaid_count,
        'total_revenue_bookings': total_revenue_bookings,
        'total_booking_count': all_bookings.count(),
        'start_date': start_date,
        'end_date': end_date,
        'days_in_period': days_in_period,
        'avg_daily_revenue': avg_daily_revenue,
        'bookings': all_bookings  # Show all bookings in the table
    }
    
    return render(request, 'hotel/revenue_report.html', context)

def generate_revenue_pdf(request, bookings, start_date, end_date, total_revenue, revenue_by_room_type, monthly_revenue):
    # Get stats for cancelled bookings
    cancelled_paid_count = bookings.filter(status='cancelled', payment_status=True).count()
    cancelled_unpaid_count = bookings.filter(status='cancelled', payment_status=False).count()
    revenue_bookings_count = bookings.filter(
        Q(~Q(status='cancelled')) | Q(status='cancelled', payment_status=True)
    ).count()
    active_bookings_count = bookings.exclude(status='cancelled').count()
    
    template_path = 'hotel/revenue_report_pdf.html'
    context = {
        'bookings': bookings,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'revenue_by_room_type': revenue_by_room_type,
        'monthly_revenue': monthly_revenue,
        'cancelled_paid_count': cancelled_paid_count,
        'cancelled_unpaid_count': cancelled_unpaid_count,
        'revenue_bookings_count': revenue_bookings_count,
        'total_bookings': bookings.count(),
        'active_bookings_count': active_bookings_count
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="revenue_report_{start_date}_{end_date}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def generate_revenue_excel(request, bookings, start_date, end_date, total_revenue, revenue_by_room_type, monthly_revenue):
    # Filter bookings by date range if provided in URL params
    date_range_start = request.GET.get('date_start')
    date_range_end = request.GET.get('date_end')
    
    if date_range_start and date_range_end:
        try:
            filter_start = datetime.strptime(date_range_start, '%Y-%m-%d').date()
            filter_end = datetime.strptime(date_range_end, '%Y-%m-%d').date()
            
            # Filter bookings that have any overlap with the specified date range
            bookings = bookings.filter(
                Q(check_in_date__lte=filter_end) & Q(check_out_date__gte=filter_start)
            )
            
            # Update start_date and end_date for the filename
            start_date = filter_start
            end_date = filter_end
        except ValueError:
            # Invalid date format, ignore the filter
            pass
    
    # Get stats for cancelled bookings
    cancelled_paid_count = bookings.filter(status='cancelled', payment_status=True).count()
    cancelled_unpaid_count = bookings.filter(status='cancelled', payment_status=False).count()
    revenue_bookings_count = bookings.filter(
        Q(~Q(status='cancelled')) | Q(status='cancelled', payment_status=True)
    ).count()
    active_booking_count = bookings.exclude(status='cancelled').count()
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Bookings")
    
    # Define formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#3498db', 'color': 'white', 'border': 1})
    cell_format = workbook.add_format({'border': 1})
    money_format = workbook.add_format({'num_format': 'Rs#,##0.00', 'border': 1})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    paid_format = workbook.add_format({'bg_color': '#d4edda', 'border': 1})
    unpaid_format = workbook.add_format({'bg_color': '#f8d7da', 'border': 1})
    cancelled_paid_format = workbook.add_format({'bg_color': '#c3e6cb', 'border': 1})
    cancelled_unpaid_format = workbook.add_format({'bg_color': '#f5c6cb', 'border': 1})
    
    # Add title with date range
    row = 0
    worksheet.write(row, 0, f"Bookings Report: {start_date} to {end_date}", workbook.add_format({'bold': True, 'font_size': 12}))
    row += 2
    
    # Add booking details header
    worksheet.write(row, 0, "Booking ID", header_format)
    worksheet.write(row, 1, "Guest", header_format)
    worksheet.write(row, 2, "Room", header_format)
    worksheet.write(row, 3, "Check In", header_format)
    worksheet.write(row, 4, "Check Out", header_format)
    worksheet.write(row, 5, "Status", header_format)
    worksheet.write(row, 6, "Total Price", header_format)
    worksheet.write(row, 7, "Payment Status", header_format)
    worksheet.write(row, 8, "Created By", header_format)
    
    # Write booking data
    for booking in bookings:
        row += 1
        
        # Determine row format based on booking status and payment status
        row_format = cell_format
        if booking.status == 'cancelled':
            if booking.payment_status:
                row_format = cancelled_paid_format
            else:
                row_format = cancelled_unpaid_format
        elif booking.payment_status:
            row_format = paid_format
        else:
            row_format = unpaid_format
            
        worksheet.write(row, 0, str(booking.pk), row_format)
        worksheet.write(row, 1, booking.guest.full_name, row_format)
        worksheet.write(row, 2, f"{booking.room.number} ({booking.room.room_type.name})", row_format)
        
        try:
            check_in_date = booking.check_in_date.strftime('%Y-%m-%d')
            check_out_date = booking.check_out_date.strftime('%Y-%m-%d')
            worksheet.write(row, 3, booking.check_in_date, date_format)
            worksheet.write(row, 4, booking.check_out_date, date_format)
        except AttributeError:
            check_in_date = "N/A"
            check_out_date = "N/A"
            worksheet.write(row, 3, check_in_date, row_format)
            worksheet.write(row, 4, check_out_date, row_format)
            
        worksheet.write(row, 5, booking.get_status_display(), row_format)
        worksheet.write(row, 6, float(booking.total_price), money_format)
        
        # Handle payment status correctly
        if booking.status == 'cancelled':
            if booking.payment_status:
                payment_status = 'Cancelled - Paid'
            else:
                payment_status = 'Cancelled - Unpaid'
        else:
            payment_status = 'Paid' if booking.payment_status else 'Unpaid'
            
        worksheet.write(row, 7, payment_status, row_format)
        
        # Add Created By info
        if hasattr(booking, 'created_by') and booking.created_by:
            role = getattr(booking.created_by.profile, 'role', 'admin' if booking.created_by.is_superuser else 'staff')
            created_by = f"{booking.created_by.username} ({role})"
        else:
            created_by = 'N/A'
        worksheet.write(row, 8, created_by, row_format)
    
    # Add legend at the bottom
    legend_row = row + 3
    worksheet.write(legend_row, 0, "Color Legend:", workbook.add_format({'bold': True}))
    worksheet.write(legend_row + 1, 0, "Active, Paid", paid_format)
    worksheet.write(legend_row + 2, 0, "Active, Unpaid", unpaid_format)
    worksheet.write(legend_row + 3, 0, "Cancelled, Paid", cancelled_paid_format)
    worksheet.write(legend_row + 4, 0, "Cancelled, Unpaid", cancelled_unpaid_format)
    
    # Auto-adjust column widths
    for col_num in range(9):
        worksheet.set_column(col_num, col_num, 15)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="bookings_{start_date}_{end_date}.xlsx"'
    return response

@login_required
def guest_analytics(request):
    # Get all guests
    guests = Guest.objects.all()
    total_guests = guests.count()
    
    # Calculate new guests in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_guests = guests.filter(created_at__gte=thirty_days_ago).count()
    
    # Calculate returning guests (guests with more than one booking)
    returning_guests_count = 0
    returning_guests = []
    
    for guest in guests:
        booking_count = guest.bookings.count()
        if booking_count > 1:
            returning_guests_count += 1
            returning_guests.append({
                'guest': guest,
                'booking_count': booking_count
            })
    
    # Sort returning guests by booking count
    returning_guests.sort(key=lambda x: x['booking_count'], reverse=True)
    
    # Get top 10 returning guests
    top_returning_guests = returning_guests[:10]
    
    # Calculate guest country distribution
    country_distribution = {}
    for choice in Guest.COUNTRY_CHOICES:
        code, name = choice
        count = guests.filter(country=code).count()
        if count > 0:
            country_distribution[name] = count
    
    # Calculate average length of stay
    bookings = Booking.objects.filter(status__in=['checked_in', 'checked_out'])
    total_nights = 0
    for booking in bookings:
        if booking.check_in_date and booking.check_out_date:
            nights = (booking.check_out_date - booking.check_in_date).days
            total_nights += nights
    
    avg_stay = total_nights / bookings.count() if bookings.count() > 0 else 0
    
    # Calculate guest satisfaction metrics
    # This is a placeholder - adjust according to your actual data model
    # You might need to extend your model to include guest feedback/ratings
    satisfaction_metrics = {
        'excellent': 75,
        'good': 15,
        'average': 7,
        'poor': 3
    }
    
    # Calculate guest source distribution 
    # This is a placeholder - adjust according to your actual data model
    guest_sources = {
        'Direct': 45,
        'Online Travel Agency': 30,
        'Corporate': 15,
        'Referral': 10
    }
    
    context = {
        'total_guests': total_guests,
        'new_guests': new_guests,
        'returning_guests_count': returning_guests_count,
        'top_returning_guests': top_returning_guests,
        'country_distribution': country_distribution,
        'avg_stay': round(avg_stay, 1),
        'satisfaction_metrics': satisfaction_metrics,
        'guest_sources': guest_sources
    }
    
    return render(request, 'hotel/guest_analytics.html', context)

@login_required
def theme_settings(request):
    # Get or create theme settings for the user
    theme_settings, created = ThemeSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ThemeSettingsForm(request.POST, instance=theme_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theme settings updated successfully')
            return redirect('theme_settings')
    else:
        form = ThemeSettingsForm(instance=theme_settings)
    
    return render(request, 'hotel/theme_settings.html', {'form': form})

# PDF Generation
@login_required
def booking_receipt_pdf(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    hotel_info = HotelInfo.get_default()
    template_path = 'hotel/booking_receipt_pdf.html'
    context = {
        'booking': booking,
        'hotel_info': hotel_info
    }
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # Set to inline to display in browser instead of attachment for download
    response['Content-Disposition'] = f'inline; filename="booking_receipt_{booking.booking_id}.pdf"'
    
    # Create a PDF
    template = get_template(template_path)
    html = template.render(context)
    
    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Return PDF document if it was successful
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@admin_required
def hotel_info(request):
    """View for updating hotel information"""
    # Get or create hotel info record
    hotel_info = HotelInfo.get_default()
    
    if request.method == 'POST':
        form = HotelInfoForm(request.POST, instance=hotel_info)
        if form.is_valid():
            form.save()
        messages.success(request, 'Hotel information updated successfully!')
        return redirect('dashboard')
    else:
        form = HotelInfoForm(instance=hotel_info)
    
    return render(request, 'hotel/hotel_info_form.html', {'form': form})

@login_required
@admin_required
def update_payment_status(request, pk):
    """Update the payment status of a booking via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            booking = get_object_or_404(Booking, pk=pk)
            
            # Get the current and new payment status
            current_status = booking.payment_status
            new_status = request.POST.get('payment_status') == 'true'
            
            # Only allow changes from unpaid to paid, not from paid to unpaid
            if current_status is False or new_status is True:
                booking.payment_status = new_status
                booking.save(update_fields=['payment_status'])
                
                # Return appropriate status based on the booking status
                status_html = ''
                if booking.status == 'cancelled':
                    status_html = '<span class="badge bg-danger">Cancelled - Unpaid</span>'
                elif booking.payment_status:
                    status_html = '<span class="badge bg-success">Paid</span>'
                else:
                    status_html = '<span class="badge bg-warning text-dark">Unpaid</span>'
                
                return JsonResponse({
                    'success': True, 
                    'payment_status': booking.payment_status,
                    'status_html': status_html
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot change payment status from paid to unpaid'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
