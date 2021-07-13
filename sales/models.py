from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from payments.models import Payment
from orders.models import Order


class Sale(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='sale'
    )
    description = models.TextField(blank=True, null=True)
    order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Sale')
        verbose_name_plural = _('Sales')
        ordering = ('-transaction_date', )

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.description = self.payment.order.description
        super().save(*args, **kwargs)
        if self.payment.order.order_type == Order.CUSTOM:
            kwargs = {
                'description': self.payment.order.description,
                'quantity': 1,
                'price': self.payment.order.custom_cost,
            }
            SaleItem.objects.create(**kwargs)
        else:
            for order_item in self.payment.order.order_items.all():
                kwargs = {
                    'description': order_item.item.product,
                    'unit': order_item.item.unit,
                    'price': order_item.item.price
                }
                SaleItem.objects.create(**kwargs)


class SaleItem(models.Model):

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
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='sale_items'
    )
    description = models.TextField()
    unit = models.CharField(
        max_length=2,
        choices=UNIT_CHOICES,
        default=PCS,
        help_text=_('Measurement unit.')
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _('Sale Item')
        verbose_name_plural = _('Sale Items')

    def __str__(self):
        return self.description

