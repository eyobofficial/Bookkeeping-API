from uuid import uuid4
from django.core.exceptions import ValidationError

from django.db import models
from django.utils.translation import gettext_lazy as _

from business.models import BusinessAccount
from customers.models import Customer
from inventory.models import Stock


class Order(models.Model):
    """
    Customer orders for a business account.
    """

    # Order Types
    FROM_LIST = 0
    CUSTOM = 1

    ORDER_TYPES_CHOICES = (
        (FROM_LIST, _('from list')),
        (CUSTOM, _('custom order'))
    )

    # Payment Options
    CASH = 'CASH'
    BANK = 'BANK'
    CARD = 'CARD'
    CREDIT = 'CREDIT'

    PAYMENT_CHOICES = (
        (CASH, _('Cash')),
        (BANK, _('Bank Transfer')),
        (CARD, _('Card Transfer')),
        (CREDIT, _('Pay Later'))
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    order_type = models.IntegerField(choices=ORDER_TYPES_CHOICES)
    business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    custom_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text=_('A total price offer for custom order.')
    )
    mode_of_payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    pay_later_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(_('completed'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Customer Order')
        verbose_name_plural = _('Customer Orders')
        default_related_name = 'orders'
        ordering = ('-created_at', )

    def __str__(self):
        return self.customer.name

    @property
    def total_cost(self):
        if self.order_type == Order.FROM_LIST:
            items = self.order_items.all()
            return sum([item.cost for item in items], 2)
        return self.custom_cost


class OrderItem(models.Model):
    """
    A product item for a customer order with the type `from list`.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        default_related_name = 'order_items'
        ordering = ('created_at', )

    def __str__(self):
        return self.order.customer.name

    @property
    def cost(self):
        """
        Sub-total of the order item.
        """
        return round(self.quantity * self.item.price, 2)
