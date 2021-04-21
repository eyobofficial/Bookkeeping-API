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

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        default_related_name = 'users'

    def __str__(self):
        return str(self.phone_number)

    @property
    def full_name(self):
        """Getter property for getting a full name."""
        return f'{self.first_name} {self.last_name}'
