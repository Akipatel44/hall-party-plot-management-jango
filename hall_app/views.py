from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Sum
from .models import (
    Hall, HallAmenity, Amenity, Booking, Payment, Cancellation, 
    CancellationPolicy, CateringService, BookingCatering, 
    Feedback, Notification, Staff, HallStaff, MaintenanceRequest,
    HallImage  # Make sure this model exists
)
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm, HallForm, 
    HallImageForm, HallSearchForm, BookingForm, CateringSelectionForm, 
    PaymentForm, CancellationForm, FeedbackForm, MaintenanceRequestForm, StaffForm,
    AmenityForm
)
# Corrected formset imports
from django.forms import inlineformset_factory

# This should use HallImage model, not HallAmenity
HallImageFormSet = inlineformset_factory(Hall, HallImage, form=HallImageForm, extra=3)

# This is for amenities
HallAmenityFormSet = inlineformset_factory(Hall, HallAmenity, fields=['amenity'], extra=3)

import uuid

# Rest of your code remains the same...

# Home Page View
def home(request):
    halls = Hall.objects.all()[:6]  # Get 6 halls for featured section
    
    # Prepare hall data with primary images
    for hall in halls:
        primary_image = hall.images.filter(is_primary=True).first()
        hall.primary_image = primary_image
    
    context = {
        'halls': halls,
    }
    return render(request, 'hall_app/home.html', context)

def custom_logout(request):
    logout(request)
    return redirect('home')
    
# About Page View
def about(request):
    return render(request, 'hall_app/about.html')

# Contact Page View
def contact(request):
    return render(request, 'hall_app/contact.html')

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'hall_app/register.html', {'form': form})

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    
    # Check if the user is authorized to cancel this booking
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('dashboard')
    
    # Check if the booking can be cancelled
    if booking.status == 'cancelled':
        messages.error(request, "This booking is already cancelled.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        
        # Create cancellation record
        cancellation = Cancellation.objects.create(
            booking=booking,
            reason=reason,
            cancelled_by=request.user
        )
        
        # Update booking status
        booking.status = 'cancelled'
        booking.save()
        
        # Create notification
        Notification.objects.create(
            user=booking.user,
            title="Booking Cancelled",
            message=f"Your booking {booking.booking_id} has been cancelled.",
            notification_type='cancellation'
        )
        
        messages.success(request, "Booking cancelled successfully.")
        return redirect('dashboard')
    
    return render(request, 'hall_app/booking_cancel.html', {'booking': booking})

# User Profile View
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'hall_app/profile.html', context)

# Hall List View
def hall_list(request):
    halls = Hall.objects.all()
    form = HallSearchForm(request.GET or None)
    
    if form.is_valid():
        event_date = form.cleaned_data.get('event_date')
        min_capacity = form.cleaned_data.get('min_capacity')
        max_price = form.cleaned_data.get('max_price')
        amenities = form.cleaned_data.get('amenities')
        
        if event_date:
            # Filter out halls that are already booked on this date
            booked_halls = Booking.objects.filter(
                event_date=event_date,
                is_canceled=False
            ).values_list('hall', flat=True)
            halls = halls.exclude(hall_id__in=booked_halls)
        
        if min_capacity:
            halls = halls.filter(capacity__gte=min_capacity)
            
        if max_price:
            halls = halls.filter(price_per_hour__lte=max_price)
            
        if amenities:
            for amenity_id in amenities:
                halls = halls.filter(hallamenity__amenity_id=amenity_id)
    
    context = {
        'halls': halls,
        'form': form,
    }
    return render(request, 'hall_app/hall_list.html', context)

# Hall Detail View
def hall_detail(request, hall_id):
    hall = get_object_or_404(Hall, pk=hall_id)
    amenities = HallAmenity.objects.filter(hall=hall).select_related('amenity')
    total_amount = hall.price_per_hour * 4
    
    # Check if hall is available for booking
    today = timezone.now().date()
    booked_dates = Booking.objects.filter(
        hall=hall,
        event_date__gte=today,
        is_canceled=False
    ).values_list('event_date', flat=True)
    
    booking_form = BookingForm(hall=hall, user=request.user if request.user.is_authenticated else None)
    catering_form = CateringSelectionForm()
    catering_services = CateringService.objects.all()
    
    context = {
        'hall': hall,
        'amenities': amenities,
        'booked_dates': list(booked_dates),
        'total_amount': total_amount,
        'booking_form': booking_form,
        'catering_form': catering_form,
        'catering_services': catering_services,
    }
    return render(request, 'hall_app/hall_detail.html', context)

# Booking Create View
@login_required
def booking_create(request, hall_id):
    hall = get_object_or_404(Hall, pk=hall_id)
    
    if request.method == 'POST':
        booking_form = BookingForm(request.POST, hall=hall, user=request.user)
        catering_form = CateringSelectionForm(request.POST)
        
        if booking_form.is_valid() and catering_form.is_valid():
            # Check if hall is available on the selected date
            event_date = booking_form.cleaned_data['event_date']
            existing_bookings = Booking.objects.filter(
                hall=hall,
                event_date=event_date,
                is_canceled=False
            )
            
            if existing_bookings.exists():
                messages.error(request, "This hall is already booked for the selected date.")
                return redirect('hall_detail', hall_id=hall_id)
            
            with transaction.atomic():
                # Create booking
                booking = booking_form.save(commit=False)
                booking.booking_id = f"B{str(uuid.uuid4().int)[:4]}"
                booking.customer = request.user
                booking.hall = hall
                booking.booking_date = timezone.now().date()
                
                # Calculate total amount
                total_hours = booking_form.cleaned_data['total_hours']
                total_amount = hall.price_per_hour * total_hours
                
                # Add catering cost if selected
                catering_service = catering_form.cleaned_data.get('catering_service')
                number_of_people = catering_form.cleaned_data.get('number_of_people')
                
                if catering_service and number_of_people:
                    catering_cost = catering_service.price_per_person * number_of_people
                    total_amount += catering_cost
                
                booking.total_amount = total_amount
                booking.save()
                
                # Create catering booking if selected
                if catering_service and number_of_people:
                    BookingCatering.objects.create(
                        booking=booking,
                        catering_service=catering_service,
                        number_of_people=number_of_people,
                        total_cost=catering_cost
                    )
                
                # Create notification
                Notification.objects.create(
                    notification_id=f"N{str(uuid.uuid4().int)[:4]}",
                    customer=request.user,
                    booking=booking,
                    notification_date=timezone.now().date(),
                    notification_type='booking',
                    message=f"Your booking for {hall.hall_name} on {event_date} has been confirmed."
                )
                
                messages.success(request, "Booking created successfully. Proceed to payment.")
                return redirect('booking_payment', booking_id=booking.booking_id)
    else:
        booking_form = BookingForm(hall=hall, user=request.user)
        catering_form = CateringSelectionForm()
    
    context = {
        'hall': hall,
        'booking_form': booking_form,
        'catering_form': catering_form,
    }
    return render(request, 'hall_app/booking_form.html', context)

# Booking Payment View
@login_required
def booking_payment(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    
    if booking.is_canceled:
        messages.error(request, "This booking has been canceled.")
        return redirect('dashboard')
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(booking=booking, payment_status='completed').first()
    if existing_payment:
        messages.info(request, "Payment has already been made for this booking.")
        return redirect('booking_confirmation', booking_id=booking_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_id = f"P{str(uuid.uuid4().int)[:4]}"
            payment.booking = booking
            payment.payment_date = timezone.now().date()
            payment.amount_paid = booking.total_amount
            payment.payment_status = 'completed'
            payment.save()
            
            # Create notification
            Notification.objects.create(
                notification_id=f"N{str(uuid.uuid4().int)[:4]}",
                customer=request.user,
                booking=booking,
                notification_date=timezone.now().date(),
                notification_type='booking',
                message=f"Payment of ₹{booking.total_amount} for your booking has been received."
            )
            
            messages.success(request, "Payment successful!")
            return redirect('booking_confirmation', booking_id=booking_id)
    else:
        form = PaymentForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'hall_app/payment.html', context)

# Booking Confirmation View
@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    payment = Payment.objects.filter(booking=booking).first()
    catering = BookingCatering.objects.filter(booking=booking).first()
    
    context = {
        'booking': booking,
        'payment': payment,
        'catering': catering,
    }
    return render(request, 'hall_app/booking_confirmation.html', context)

# Booking Cancel View
@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    
    if booking.is_canceled:
        messages.error(request, "This booking is already canceled.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CancellationForm(request.POST)
        if form.is_valid():
            cancellation = form.save(commit=False)
            cancellation.cancellation_id = f"C{str(uuid.uuid4().int)[:4]}"
            cancellation.booking = booking
            cancellation.cancellation_date = timezone.now().date()
            
            # Calculate refund based on cancellation policy
            days_to_event = (booking.event_date - timezone.now().date()).days
            
            # Get applicable policy
            policy = CancellationPolicy.objects.filter(
                booking_type='standard',
                days_before_event__lte=days_to_event
            ).order_by('-days_before_event').first()
            
            if policy:
                refund_percentage = policy.refund_percentage
                refund_amount = (booking.total_amount * refund_percentage) / 100
            else:
                refund_amount = 0
            
            cancellation.refund_amount = refund_amount
            cancellation.cancellation_status = 'pending'
            cancellation.save()
            
            # Update booking status
            booking.is_canceled = True
            booking.save()
            
            # Create notification
            Notification.objects.create(
                notification_id=f"N{str(uuid.uuid4().int)[:4]}",
                customer=request.user,
                booking=booking,
                notification_date=timezone.now().date(),
                notification_type='cancellation',
                message=f"Your booking cancellation request has been submitted. Refund amount: ₹{refund_amount}"
            )
            
            messages.success(request, "Booking canceled successfully. Refund process initiated.")
            return redirect('dashboard')
    else:
        form = CancellationForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'hall_app/booking_cancel.html', context)

# Dashboard View
@login_required
def dashboard(request):
    user = request.user
    user_profile = user.profile
    
    if user_profile.user_type == 'customer':
        return customer_dashboard(request)
    elif user_profile.user_type in ['admin', 'staff']:
        return admin_dashboard(request)
    else:
        return redirect('home')

# Customer Dashboard View
def customer_dashboard(request):
    user = request.user
    today = timezone.now().date()
    
    # Get upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        customer=user,
        event_date__gte=today,
        is_canceled=False
    ).order_by('event_date')
    
    # Get past bookings
    past_bookings = Booking.objects.filter(
        customer=user,
        event_date__lt=today
    ).order_by('-event_date')
    
    # Get recent payments
    recent_payments = Payment.objects.filter(
        booking__customer=user
    ).order_by('-payment_date')[:5]
    
    # Get unread notifications
    notifications = Notification.objects.filter(
        customer=user,
        is_read=False
    ).order_by('-notification_date')
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'recent_payments': recent_payments,
        'notifications': notifications,
    }
    return render(request, 'hall_app/customer_dashboard.html', context)

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_hall_list(request):
    halls = Hall.objects.all().order_by('-created_at')
    return render(request, 'hall_app/admin_hall_list.html', {'halls': halls})

# Admin Dashboard View
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Add a debug print statement
    print("Admin dashboard view is being called!")
    
    hall_count = Hall.objects.count()
    active_bookings = Booking.objects.filter(is_canceled=False, event_date__gte=timezone.now().date()).count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    recent_bookings = Booking.objects.order_by('-booking_date')[:5]
    pending_cancellations = Cancellation.objects.filter(cancellation_status='pending')
    maintenance_requests = MaintenanceRequest.objects.filter(resolution_status__in=['pending', 'in_progress'])
    
    context = {
        'hall_count': hall_count,
        'active_bookings': active_bookings,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'pending_cancellations': pending_cancellations,
        'maintenance_requests': maintenance_requests,
    }
    
    return render(request, 'hall_app/admin_dashboard.html', context)

# Mark Notification as Read View
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, customer=request.user)
    notification.is_read = True
    notification.save()
    return redirect('dashboard')

# Feedback Create View
@login_required
def feedback_create(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    
    # Check if feedback already exists
    existing_feedback = Feedback.objects.filter(booking=booking).first()
    if existing_feedback:
        messages.info(request, "You have already provided feedback for this booking.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.feedback_id = f"F{str(uuid.uuid4().int)[:4]}"
            feedback.booking = booking
            feedback.customer = request.user
            feedback.feedback_date = timezone.now().date()
            feedback.save()
            
            messages.success(request, "Thank you for your feedback!")
            return redirect('dashboard')
    else:
        form = FeedbackForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'hall_app/feedback_form.html', context)

# Maintenance Request Create View
@login_required
def maintenance_request_create(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.request_id = f"M{str(uuid.uuid4().int)[:4]}"
            maintenance_request.request_date = timezone.now().date()
            maintenance_request.resolution_status = 'pending'
            maintenance_request.save()
            
            messages.success(request, "Maintenance request submitted successfully.")
            return redirect('admin_dashboard')
    else:
        form = MaintenanceRequestForm()
    
    context = {
        'form': form,
    }
    return render(request, 'hall_app/maintenance_request_form.html', context)

# Staff Management Views
@login_required
def staff_list(request):
    if request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    staff = Staff.objects.all()
    context = {
        'staff': staff,
    }
    return render(request, 'hall_app/staff_list.html', context)

@login_required
def staff_create(request):
    if request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            # Create a user for the staff member
            username = f"staff_{staff.staff_id}"
            user = User.objects.create_user(username=username, password="defaultpassword")
            user.profile.user_type = 'staff'
            user.profile.save()
            
            staff.user = user
            staff.save()
            
            messages.success(request, "Staff member added successfully.")
            return redirect('staff_list')
    else:
        form = StaffForm()
    
    context = {
        'form': form,
    }
    return render(request, 'hall_app/staff_form.html', context)

# Hall Management Views
# Create Hall
@login_required
@user_passes_test(is_admin)
def hall_create(request):
    if request.method == 'POST':
        hall_form = HallForm(request.POST)
        if hall_form.is_valid():
            with transaction.atomic():
                hall = hall_form.save()
                
                # Process hall images
                image_formset = HallImageFormSet(request.POST, request.FILES, instance=hall)
                if image_formset.is_valid():
                    image_formset.save()
                
                # Process hall amenities
                amenity_formset = HallAmenityFormSet(request.POST, instance=hall)
                if amenity_formset.is_valid():
                    amenity_formset.save()
                
                messages.success(request, f'Hall "{hall.hall_name}" has been created successfully!')
                return redirect('admin_hall_list')
    else:
        hall_form = HallForm()
        image_formset = HallImageFormSet()
        amenity_formset = HallAmenityFormSet()
    
    context = {
        'hall_form': hall_form,
        'image_formset': image_formset,
        'amenity_formset': amenity_formset,
        'title': 'Add New Hall'
    }
    
    return render(request, 'hall_app/hall_form.html', context)

@login_required
@user_passes_test(is_admin)
def hall_update(request, hall_id):
    hall = get_object_or_404(Hall, hall_id=hall_id)
    
    if request.method == 'POST':
        hall_form = HallForm(request.POST, instance=hall)
        if hall_form.is_valid():
            with transaction.atomic():
                hall = hall_form.save()
                
                # Process hall images
                image_formset = HallImageFormSet(request.POST, request.FILES, instance=hall)
                if image_formset.is_valid():
                    image_formset.save()
                
                # Process hall amenities
                amenity_formset = HallAmenityFormSet(request.POST, instance=hall)
                if amenity_formset.is_valid():
                    amenity_formset.save()
                
                messages.success(request, f'Hall "{hall.hall_name}" has been updated successfully!')
                return redirect('admin_hall_list')
    else:
        hall_form = HallForm(instance=hall)
        image_formset = HallImageFormSet(instance=hall)
        amenity_formset = HallAmenityFormSet(instance=hall)
    
    context = {
        'hall_form': hall_form,
        'image_formset': image_formset,
        'amenity_formset': amenity_formset,
        'hall': hall,
        'title': 'Update Hall'
    }
    
    return render(request, 'hall_app/hall_form.html', context)

@login_required
@user_passes_test(is_admin)
def hall_delete(request, hall_id):
    hall = get_object_or_404(Hall, hall_id=hall_id)
    
    if request.method == 'POST':
        hall_name = hall.hall_name
        hall.delete()
        messages.success(request, f'Hall "{hall_name}" has been deleted successfully!')
        return redirect('admin_hall_list')
    
    return render(request, 'hall_app/hall_confirm_delete.html', {'hall': hall})

@login_required
@user_passes_test(is_admin)
def admin_hall_detail(request, hall_id):
    hall = get_object_or_404(Hall, hall_id=hall_id)
    images = hall.images.all()
    amenities = hall.hall_amenities.all().select_related('amenity')
    
    # Get bookings for this hall
    bookings = Booking.objects.filter(hall=hall).order_by('-event_date')
    
    context = {
        'hall': hall,
        'images': images,
        'amenities': amenities,
        'bookings': bookings
    }
    
    return render(request, 'hall_app/admin_hall_detail.html', context)

@login_required
@user_passes_test(is_admin)
def amenity_list(request):
    amenities = Amenity.objects.all()
    return render(request, 'hall_app/amenity_list.html', {'amenities': amenities})

@login_required
@user_passes_test(is_admin)
def amenity_create(request):
    if request.method == 'POST':
        form = AmenityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Amenity created successfully!')
            return redirect('amenity_list')
    else:
        form = AmenityForm()
    
    return render(request, 'hall_app/amenity_form.html', {'form': form, 'title': 'Add Amenity'})

@login_required
@user_passes_test(is_admin)
def amenity_update(request, amenity_id):
    amenity = get_object_or_404(Amenity, amenity_id=amenity_id)
    
    if request.method == 'POST':
        form = AmenityForm(request.POST, instance=amenity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Amenity updated successfully!')
            return redirect('amenity_list')
    else:
        form = AmenityForm(instance=amenity)
    
    return render(request, 'hall_app/amenity_form.html', {'form': form, 'title': 'Update Amenity'})

@login_required
@user_passes_test(is_admin)
def amenity_delete(request, amenity_id):
    amenity = get_object_or_404(Amenity, amenity_id=amenity_id)
    
    if request.method == 'POST':
        amenity_name = amenity.amenity_name
        amenity.delete()
        messages.success(request, f'Amenity "{amenity_name}" has been deleted successfully!')
        return redirect('amenity_list')
    
    return render(request, 'hall_app/amenity_confirm_delete.html', {'amenity': amenity})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')