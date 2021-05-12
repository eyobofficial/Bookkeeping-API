from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Default custom user.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email = models.EmailField('email address', unique=True, null=True)
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
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    profile_photo = models.ImageField(
        upload_to='profiles',
        null=True, blank=True
    )
    bio = models.TextField(blank=True)
    updated_at = models.DateTimeField('last updated date', auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.phone_number}'


class Setting(models.Model):
    """
    User specific settings, configurations, and preferences.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=30, blank=True)
    updated_at = models.DateTimeField('last updated date', auto_now=True)

    class Meta:
        verbose_name = 'User Setting'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f'{self.user.phone_number}'

