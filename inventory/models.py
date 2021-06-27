from uuid import uuid4

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from business.models import BusinessAccount
from shared.models import PhotoUpload


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
    photo = models.OneToOneField(
        PhotoUpload,
        on_delete=models.CASCADE,
        related_name='stock_photo',
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product Stock')
        verbose_name_plural = _('Product Stocks')

    def __str__(self):
        return self.product

    @transaction.atomic
    def sell(self, quantity):
        """
        Deduct quantity from the stock and add it to the related
        `sold` instance.
        """
        self.quantity -= quantity
        self.save()

        self.sold.quantity += quantity
        self.sold.save()


class Sold(models.Model):
    """
    Track sold inventory items.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    stock = models.OneToOneField(
        Stock,
        on_delete=models.CASCADE,
        related_name='sold'
    )
    quantity = models.PositiveIntegerField(_('quantity sold'), default=0)
    sales_date = models.DateField(
        auto_now=True,
        help_text=_('last sales date')
    )

    class Meta:
        verbose_name = _('Product Sold')
        verbose_name_plural = _('Products Sold')

    def __str__(self):
        return self.stock.product
