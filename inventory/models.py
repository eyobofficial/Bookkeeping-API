from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from business.models import BusinessAccount


class Stock(models.Model):

    # Measurement units
    PCS = 'pc'
    KILOGRAMS = 'kg'
    LITERS = 'lt'
    METERS = 'mt'

    UNIT_CHOICES = (
        (PCS, _('pcs')),
        (KILOGRAMS, _('kilograms')),
        (LITERS, _('lt')),
        (METERS, _('mt')),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    product = models.CharField(_('product name'), max_length=100)
    unit = models.CharField(
        max_length=2,
        choices=UNIT_CHOICES,
        help_text=_('Measurement unit.')
    )
    quantity = models.PositiveIntegerField(help_text=_('Quantity left.'))
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product Stock')
        verbose_name_plural = _('Product Stocks')

    def __str__(self):
        return self.product

