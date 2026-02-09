"""
Forms for Cricket Slot Booking System
"""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Slot, Booking


class RegisterForm(forms.Form):
    """
    User Registration Form
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'required': 'required',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'required': 'required',
        })
    )
    password1 = forms.CharField(
        label='Password',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (min 6 characters)',
            'required': 'required',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': 'required',
        })
    )
    
    def clean_username(self):
        """Validate username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        """Validate email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class BookingForm(forms.ModelForm):
    """
    Slot Booking Form
    """
    class Meta:
        model = Booking
        fields = []  # No fields needed - user and slot are pre-selected
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom styling if needed
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
