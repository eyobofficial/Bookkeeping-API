import inflect
from uuid import uuid4
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from drf_yasg.utils import swagger_serializer_method
from weasyprint import HTML

from business.models import BusinessAccount
from customers.models import Customer
from inventory.models import Stock


class Order(models.Model):
    """
    Customer orders for a business account.
    """

    # Order Types
    FROM_LIST = 'FROM_LIST'
    CUSTOM = 'CUSTOM'

    ORDER_TYPES_CHOICES = (
        (FROM_LIST, _('from list')),
        (CUSTOM, _('custom order'))
    )

    # Status Choices
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    STATUS_CHOICES = (
        (OPEN, _('Open')),
        (CLOSED, _('Closed'))
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES_CHOICES)
    business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField(
        blank=True, null=True,
        help_text='Required for `CUSTOM` order types to describe the sold items.'
    )
    custom_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text=_('A total price offer for custom order.')
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Customer Order')
        verbose_name_plural = _('Customer Orders')
        default_related_name = 'orders'
        ordering = ('-created_at', )

    def __str__(self):
        return self.customer.name

    @cached_property
    def cost(self):
        """
        Return a total cost of the order.

        If order_type is `FROM_LIST`, return the sum of the order
        items cost. But if order_type is `CUSTOM`, return the user
        provided cost.
        """
        if self.order_type == Order.FROM_LIST:
            items = self.order_items.all()
            total = sum([item.cost for item in items])
            return round(total, 2)
        return self.custom_cost

    @cached_property
    def taxes(self):
        """
        Returns the TAX name, percentage, and tax amount of a Business Account
        """
        taxes = self.business_account.taxes.filter(active=True)
        return [dict(name=tax.name,
                      percentage=tax.percentage,
                      amount=tax.get_tax_amount(self.cost))
                      for tax in taxes]

    @cached_property
    def total_tax_percentage(self):
        """
        Returns the sum of all TAX percentages that are applied.
        """
        total = sum([tax['percentage'] for tax in self.taxes])
        return round(total, 2)

    @cached_property
    def total_tax_amount(self):
        """
        Returns the TAX amount to be deducted.
        """
        total = sum([tax['amount'] for tax in self.taxes])
        return round(total, 2)

    @cached_property
    def total_amount(self):
        """
        Returns the total order amount after tax.
        """
        total = self.cost + self.total_tax_amount
        return round(total, 2)

    def save_order_items_description(self):
        """
        Saves an appropriate description field for `FROM_LIST` orders.

        If order is of type `FROM_LIST` (i.e. created from inventory),
        the value of the `description` field should be calculated from the
        selected order items.
        """
        if self.order_type == Order.CUSTOM:
            return

        qs = self.order_items.all()
        p = inflect.engine()

        order_items = {}

        for order_item in qs:
            product = order_item.item.product
            count = order_items.get(product, 0)
            order_items[product] = count + order_item.quantity

        description = ', '.join(
            [
                f'{Order.stringfy_num(quantity)} {p.plural(product, quantity)}'
                for product, quantity in order_items.items()
            ]
        )
        self.description = description
        self.save()

    @staticmethod
    def stringfy_num(num):
        """
        Convert a decimal number to a human readable format.

        Examples:
          * 3.00 -> 3
          * 4.50 -> 4.5
          * 9.99 -> 9.99
        """
        whole, fraction = str(num).split('.')
        if fraction.rstrip('0') == '':
            return whole
        return '.'.join([whole, fraction.rstrip('0')])


class OrderItem(models.Model):
    """
    A product item for a customer order with the type `from list`.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        default_related_name = 'order_items'
        ordering = ('updated_at', )

    def __str__(self):
        return self.order.customer.name

    @cached_property
    def cost(self) -> float:
        """
        Sub-total of the order item.
        """
        return round(self.quantity * self.item.price, 2)

    def save(self, *args, **kwargs):
        """
        Overwrite `save` method to modify some fields.

        The following modifications are implemented:
        1. Consolidate the quantities of order item of the same order.
        2. Conditionally set the `description` field.
        """

        # 1. Consolidate quantity
        order_item = None
        qs = OrderItem.objects.filter(order=self.order, item=self.item)
        if qs.exists():
            order_item = qs.first()
            self.quantity += order_item.quantity

        super().save(*args, **kwargs)

        # Delete the previous (now duplicate) order item
        if order_item is not None:
            order_item.delete()

        # 2. Conditionally set the description field
        self.order.save_order_items_description()
