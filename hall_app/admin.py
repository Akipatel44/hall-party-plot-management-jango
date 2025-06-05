from django.contrib import admin
from .models import (
    UserProfile, Hall, HallImage, Amenity, HallAmenity,
    Booking, Payment, Cancellation, CancellationPolicy,
    Staff, HallStaff, CateringService, BookingCatering,
    MaintenanceRequest, Feedback, Notification
)

# Register models
admin.site.register(UserProfile)
admin.site.register(Hall)
admin.site.register(HallImage)
admin.site.register(Amenity)
admin.site.register(HallAmenity)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Cancellation)
admin.site.register(CancellationPolicy)
admin.site.register(Staff)
admin.site.register(HallStaff)
admin.site.register(CateringService)
admin.site.register(BookingCatering)
admin.site.register(MaintenanceRequest)
admin.site.register(Feedback)
admin.site.register(Notification)