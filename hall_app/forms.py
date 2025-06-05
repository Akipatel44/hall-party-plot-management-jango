from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    UserProfile, Hall, HallImage, Booking, Payment, 
    Cancellation, CateringService, BookingCatering, 
    Feedback, MaintenanceRequest, Staff
)
from .models import Hall, HallImage, Amenity, HallAmenity

# User Registration Form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

# User Update Form
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['contact_number', 'address']

# Hall Form
class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['hall_name', 'description', 'capacity', 'price_per_hour', 'address', 'contact_number', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

# Hall Image Form
class HallImageForm(forms.ModelForm):
    class Meta:
        model = HallImage
        fields = ['image', 'is_primary']

HallImageFormSet = forms.inlineformset_factory(
    Hall, HallImage, form=HallImageForm,
    extra=3, can_delete=True
)

# Hall Search Form
class HallSearchForm(forms.Form):
    event_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    min_capacity = forms.IntegerField(required=False, label='Minimum Capacity')
    max_price = forms.DecimalField(required=False, label='Maximum Price per Hour')
    amenities = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        super(HallSearchForm, self).__init__(*args, **kwargs)
        from .models import Amenity
        self.fields['amenities'].choices = [(amenity.amenity_id, amenity.amenity_name) for amenity in Amenity.objects.all()]

class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['amenity_name', 'description']

# Booking Form
class BookingForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Booking
        fields = ['event_date', 'total_hours']
        
    def __init__(self, *args, **kwargs):
        self.hall = kwargs.pop('hall', None)
        self.user = kwargs.pop('user', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        
    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        # Add validation to check if hall is available on this date
        from django.utils import timezone
        if event_date < timezone.now().date():
            raise forms.ValidationError("Event date cannot be in the past")
        return event_date

# Catering Selection Form
class CateringSelectionForm(forms.Form):
    catering_service = forms.ModelChoiceField(
        queryset=CateringService.objects.all(),
        required=False,
        empty_label="No catering needed"
    )
    number_of_people = forms.IntegerField(min_value=1, required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        catering_service = cleaned_data.get('catering_service')
        number_of_people = cleaned_data.get('number_of_people')
        
        if catering_service and not number_of_people:
            raise forms.ValidationError("Please specify the number of people for catering")
        
        return cleaned_data

# Payment Form
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        
# Cancellation Form
class CancellationForm(forms.ModelForm):
    class Meta:
        model = Cancellation
        fields = ['cancellation_reason']
        widgets = {
            'cancellation_reason': forms.Textarea(attrs={'rows': 3}),
        }

# Feedback Form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }

# Maintenance Request Form
class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['hall', 'issue_description']
        widgets = {
            'issue_description': forms.Textarea(attrs={'rows': 4}),
        }

# Staff Form
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id', 'contact_number', 'role', 'salary']

class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['amenity_name', 'description']

class HallAmenityForm(forms.ModelForm):
    amenity = forms.ModelChoiceField(queryset=Amenity.objects.all())
    quantity = forms.IntegerField(min_value=1)

    class Meta:
        model = HallAmenity
        fields = ['amenity', 'quantity']

HallAmenityFormSet = forms.inlineformset_factory(
    Hall, HallAmenity, form=HallAmenityForm,
    extra=3, can_delete=True
)