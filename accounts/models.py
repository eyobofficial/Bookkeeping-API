from uuid import uuid4
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from shared.models import PhotoUpload
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Default custom user.
    """
    # User Types
    BUSINESS = 1
    PARTNER = 2
    STAFF = 3

    USER_TYPEC_CHOICES = (
        (BUSINESS, _('Business Owner')),
        (PARTNER, _('Partner')),
        (STAFF, _('Staff'))
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email = models.EmailField(_('email address'), unique=True, null=True)
    phone_number = PhoneNumberField(unique=True, null=True)
    username = models.CharField(max_length=100, unique=True, null=True)
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)
    pin = models.CharField(_('PIN'), max_length=128, blank=True, null=True)
    type = models.PositiveSmallIntegerField(choices=USER_TYPEC_CHOICES, default=BUSINESS)

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

    def check_password(self, raw_password, *args, **kwargs):
        if self.type == CustomUser.BUSINESS and self.pin is not None:
            return check_password(raw_password, self.pin)
        return check_password(raw_password, self.password)

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)


class Profile(models.Model):
    """
    User profile
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    profile_photo = models.OneToOneField(
        PhotoUpload,
        null=True, blank=True,
        related_name='profile',
        on_delete=models.CASCADE
    )
    updated_at = models.DateTimeField(_('last updated date'), auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f'{self.user.phone_number}'

    @property
    def fullname(self):
        """
        Returns user full name.
        """
        return f'{self.first_name} {self.last_name}'


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
