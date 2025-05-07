from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from functools import wraps
from .models import Booking

# Admin decorator from views.py
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return view_func(request, *args, **kwargs)
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    return _wrapped_view

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
                    if booking.payment_status:
                        status_html = '<span class="badge bg-success">Cancelled - Paid</span>'
                    else:
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