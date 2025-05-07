from django import forms
from django.contrib.auth.models import User
from .models import Guest, Room, RoomType, ThemeSettings, HotelInfo

class GuestForm(forms.ModelForm):
    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('PK', 'Pakistan'),
        ('US', 'United States'),
        ('GB', 'United Kingdom'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('IN', 'India'),
        ('AE', 'United Arab Emirates'),
        ('SA', 'Saudi Arabia'),
        # Add more countries as needed
    ]

    ID_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('cnic', 'CNIC'),
        ('driving_license', 'Driving License'),
    ]

    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    id_type = forms.ChoiceField(
        choices=ID_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        required=True
    )

    class Meta:
        model = Guest
        fields = ['full_name', 'email', 'phone', 'address', 'country', 'id_type', 'id_number', 'id_document', 'vehicle_number', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'id_document': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If this is an existing guest with an ID document, make the field not required
        if self.instance and self.instance.pk and self.instance.id_document:
            self.fields['id_document'].required = False
            self.fields['id_document'].widget.attrs['required'] = False

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get('country')
        id_type = cleaned_data.get('id_type')

        # Set ID type based on country
        if country == 'PK':
            cleaned_data['id_type'] = 'cnic'
        else:
            cleaned_data['id_type'] = 'passport'

        return cleaned_data 

class UserForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('', 'Select Role'),
        ('admin', 'Administrator'),
        ('receptionist', 'Receptionist'),
    ]

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,  # Always required for new users
        help_text='Leave empty to keep current password'
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        if self.is_edit:
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Leave empty to keep current password'
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Enter a strong password'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set password if provided
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        
        # Set user permissions based on role
        role = self.cleaned_data.get('role')
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'receptionist':
            user.is_superuser = False
            user.is_staff = False
        
        if commit:
            user.save()
            # Save profile data
            if not hasattr(user, 'profile'):
                from .models import UserProfile
                UserProfile.objects.create(user=user)
            user.profile.role = self.cleaned_data['role']
            user.profile.phone = self.cleaned_data['phone']
            user.profile.address = self.cleaned_data['address']
            user.profile.save()
        
        return user 

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'room_type', 'status', 'floor', 'image', 'notes']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room number (e.g., 101)',
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'floor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter floor number',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about the room',
            }),
        }

class ThemeSettingsForm(forms.ModelForm):
    class Meta:
        model = ThemeSettings
        fields = ['primary_color', 'secondary_color', 'danger_color', 'warning_color', 'sidebar_color']
        widgets = {
            'primary_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'data-color-name': 'primary',
                'type': 'color'
            }),
            'secondary_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'data-color-name': 'secondary',
                'type': 'color'
            }),
            'danger_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'data-color-name': 'danger',
                'type': 'color'
            }),
            'warning_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'data-color-name': 'warning',
                'type': 'color'
            }),
            'sidebar_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'data-color-name': 'sidebar',
                'type': 'color'
            }),
        }

class HotelInfoForm(forms.ModelForm):
    class Meta:
        model = HotelInfo
        fields = ['name', 'address', 'phone', 'email', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Hotel Name',
            'address': 'Address',
            'phone': 'Contact Number',
            'email': 'Email Address',
            'description': 'Short Description',
        } 