from uuid import uuid4
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from shared.utils.otp import generate_otp
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Default custom user.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email = models.EmailField(_('email address'), unique=True, null=True)
    phone_number = PhoneNumberField(unique=True)

    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        default_related_name = 'users'

    def __str__(self):
        return self.phone_number.as_e164

    @property
    def full_name(self):
        """Getter property for getting a full name."""
        return f'{self.profile.first_name} {self.profile.last_name}'


class Profile(models.Model):
    """
    User profile
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = CountryField()
    postal_code = models.CharField(max_length=10, blank=True)
    profile_photo = models.ImageField(
        upload_to='profiles',
        null=True, blank=True
    )
    updated_at = models.DateTimeField(_('last updated date'), auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f'{self.user.phone_number}'


class Setting(models.Model):
    """
    User specific settings, configurations, and preferences.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    font_size = models.PositiveSmallIntegerField(
        default=11,
        help_text='Font size in pixels.'
    )
    terms_and_condition = models.BooleanField(default=False)
    updated_at = models.DateTimeField(_('last updated date'), auto_now=True)

    class Meta:
        verbose_name = _('User Setting')
        verbose_name_plural = _('User Settings')

    def __str__(self):
        return f'{self.user.phone_number}'


def get_otp_expiration():
    """
    Returns the OTP code expiration date & time.
    """
    EXPIRATION_DURATION = 30  # 30 minutes
    delta = timedelta(minutes=EXPIRATION_DURATION)
    return timezone.now() + delta


class PasswordResetCode(models.Model):
    """
    A one-time code to reset passwords.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='password_reset_codes'
    )
    otp = models.CharField(
        max_length=6,
        default=generate_otp,
        help_text='A one-time password code.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(default=get_otp_expiration)

    class Meta:
        verbose_name = 'Password Reset Code'
        verbose_name_plural = 'Password Reset Codes'
        ordering = ('-expire_at', )

    def __str__(self):
        return self.otp

    @property
    def phone_number(self):
        return self.user.phone_number
