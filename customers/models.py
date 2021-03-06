from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from business.models import BusinessAccount
from shared.models import PhotoUpload


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    business_account = models.ForeignKey(BusinessAccount,
                                         on_delete=models.CASCADE,
                                         related_name='customers')
    name = models.CharField(_('customer name'), max_length=100)
    phone_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    photo = models.OneToOneField(PhotoUpload,
                                 on_delete=models.SET_NULL,
                                 related_name='customer_photo',
                                 null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ('-created_at', )

    def __str__(self):
        return self.name
