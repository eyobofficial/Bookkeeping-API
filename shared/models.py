from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from phonenumber_field.modelfields import PhoneNumberField


class PhotoUpload(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    photo = models.ImageField(upload_to='shared', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Photo Upload')
        verbose_name_plural = _('Photo Uploads')
        ordering = ('-created_at', )

    def __str__(self):
        return str(self.id)


class TwilioService(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    phone_number = PhoneNumberField(unique=True)
    service_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Twilio Service')
        verbose_name_plural = _('Twilio Services')
        ordering = ('-created_at', )

    def __str__(self):
        return self.service_id
