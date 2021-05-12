from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from phonenumber_field.formfields import PhoneNumberField

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = PhoneNumberField(
        region=settings.PHONENUMBER_DEFAULT_REGION,
        error_messages={
            'invalid': 'Enter a valid phone number.'
        }
    )
    email = forms.EmailField(required=False, empty_value=None)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'phone_number')


class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=False, empty_value=None)

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'phone_number')


class UserRegistrationForm(CustomUserCreationForm):
    pass


class ProfileUpdateForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        region=settings.PHONENUMBER_DEFAULT_REGION,
        error_messages={
            'invalid': 'Enter a valid phone number.'
        }
    )

    class Meta:
        model = CustomUser
        fields = ('phone_number', )
