from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    USER_TYPES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# Hall Model
class Hall(models.Model):
    hall_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hall_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255, default="Address to be updated")
    contact_number = models.CharField(max_length=15, default="Not provided")
    is_active = models.BooleanField(default=True)
    # Change these datetime fields to have explicit defaults
    created_at = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add=True
    updated_at = models.DateTimeField(default=timezone.now)  # Changed from auto_now=True

    def __str__(self):
        return self.hall_name

class HallImage(models.Model):
    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hall = models.ForeignKey(Hall, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hall_images/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.hall.hall_name}"

class Amenity(models.Model):
    amenity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amenity_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.amenity_name

class HallAmenity(models.Model):
    hall = models.ForeignKey(Hall, related_name='hall_amenities', on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('hall', 'amenity')

    def __str__(self):
        return f"{self.amenity.amenity_name} for {self.hall.hall_name}"

# Discount Model
class Discount(models.Model):
    discount_id = models.CharField(max_length=5, primary_key=True)
    discount_name = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.discount_name

# Booking Model
class Booking(models.Model):
    booking_id = models.CharField(max_length=5, primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    booking_date = models.DateField()
    event_date = models.DateField()
    total_hours = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    is_canceled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Booking {self.booking_id} by {self.customer.username}"

# Payment Model
class Payment(models.Model):
    payment_id = models.CharField(max_length=5, primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    PAYMENT_METHODS = (
        ('credit card', 'Credit Card'),
        ('debit card', 'Debit Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
        ('net banking', 'Net Banking'),
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    PAYMENT_STATUS = (
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    
    def __str__(self):
        return f"Payment {self.payment_id} for Booking {self.booking.booking_id}"

# Cancellation Model
class Cancellation(models.Model):
    cancellation_id = models.CharField(max_length=5, primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    cancellation_date = models.DateField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    CANCELLATION_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    cancellation_status = models.CharField(max_length=10, choices=CANCELLATION_STATUS)
    
    def __str__(self):
        return f"Cancellation for Booking {self.booking.booking_id}"

# Cancellation Policy Model
class CancellationPolicy(models.Model):
    policy_id = models.CharField(max_length=5, primary_key=True)
    booking_type = models.CharField(max_length=20)
    days_before_event = models.IntegerField()
    refund_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.booking_type} - {self.days_before_event} days"

# Staff Model
class Staff(models.Model):
    staff_id = models.CharField(max_length=5, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    contact_number = models.CharField(max_length=15)
    ROLES = (
        ('manager', 'Manager'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('catering', 'Catering'),
        ('maintenance', 'Maintenance'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"

# Hall Staff Assignment Model
class HallStaff(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    assignment_date = models.DateField()
    
    class Meta:
        unique_together = ('hall', 'staff')
        
    def __str__(self):
        return f"{self.staff.user.get_full_name()} assigned to {self.hall.hall_name}"

# Catering Service Model
class CateringService(models.Model):
    catering_id = models.CharField(max_length=5, primary_key=True)
    service_name = models.CharField(max_length=50, unique=True)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.service_name

# Booking Catering Model
class BookingCatering(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    catering_service = models.ForeignKey(CateringService, on_delete=models.CASCADE)
    number_of_people = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('booking', 'catering_service')
        
    def __str__(self):
        return f"Catering for Booking {self.booking.booking_id}"

# Maintenance Request Model
class MaintenanceRequest(models.Model):
    request_id = models.CharField(max_length=5, primary_key=True)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    request_date = models.DateField()
    issue_description = models.TextField()
    RESOLUTION_STATUS = (
        ('pending', 'Pending'),
        ('in progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )
    resolution_status = models.CharField(max_length=20, choices=RESOLUTION_STATUS)
    resolved_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Maintenance Request {self.request_id} for {self.hall.hall_name}"

# Feedback Model
class Feedback(models.Model):
    feedback_id = models.CharField(max_length=5, primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    feedback_date = models.DateField()
    
    def __str__(self):
        return f"Feedback for Booking {self.booking.booking_id}"

# Notification Model
class Notification(models.Model):
    notification_id = models.CharField(max_length=5, primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    notification_date = models.DateField()
    NOTIFICATION_TYPES = (
        ('booking', 'Booking'),
        ('cancellation', 'Cancellation'),
        ('reminder', 'Reminder'),
        ('feedback', 'Feedback'),
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.customer.username}"