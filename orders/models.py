import inflect
from uuid import uuid4
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from weasyprint import HTML

from business.models import BusinessAccount
from customers.models import Customer
from inventory.models import Stock


class Order(models.Model):
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
    business_account = models.ForeignKey(BusinessAccount,
                                         on_delete=models.CASCADE,
                                         related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True,
                                   help_text=_('Required for `CUSTOM` order types to describe '
                                               'the sold items.'))
    custom_cost = models.DecimalField(max_digits=12, decimal_places=2,
                                      null=True, blank=True,
                                      help_text=_('A total price offer for custom order.'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
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
        if self.order_type == Order.FROM_LIST:
            items = self.order_items.all()
            total = sum([item.cost for item in items])
            return round(total, 2)
        return self.custom_cost

    @cached_property
    def taxes(self):
        taxes = self.business_account.taxes.active()
        return [dict(name=tax.name,
                      percentage=tax.percentage,
                      amount=tax.get_tax_amount(self.cost))
                      for tax in taxes]

    @cached_property
    def tax_percentage(self):
        total = sum([tax['percentage'] for tax in self.taxes])
        return round(total, 2)

    @cached_property
    def tax_amount(self):
        total = sum([tax['amount'] for tax in self.taxes])
        return round(total, 2)

    @cached_property
    def total_amount(self):
        total = self.cost + self.tax_amount
        return round(total, 2)

    def save_order_items_description(self):
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
        whole, fraction = str(num).split('.')
        if fraction.rstrip('0') == '':
            return whole
        return '.'.join([whole, fraction.rstrip('0')])


class OrderItem(models.Model):
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
    def cost(self):
        return round(self.quantity * self.item.price, 2)

    def save(self, *args, **kwargs):
        order_item = None
        qs = OrderItem.objects.filter(order=self.order, item=self.item)
        if qs.exists():
            order_item = qs.first()
            self.quantity += order_item.quantity
        super().save(*args, **kwargs)
        if order_item is not None:
            order_item.delete()
        self.order.save_order_items_description()
