from uuid import uuid4

from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.template.loader import get_template
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from weasyprint import HTML

from inventory.units import MeasurementUnit
from orders.models import Order


class Payment(models.Model):
    """
    Payment for customer orders.
    """

    # Payment Status Choices
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    FAILED  = 'FAILED'

    PAYMENT_STATUS_CHOIES = (
        (PENDING, _('Pending')),
        (COMPLETED, _('Completed')),
        (FAILED, _('Failed'))
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
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    mode_of_payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOIES,
        default=PENDING
    )
    pay_later_date = models.DateField(
        blank=True, null=True,
        help_text=_('Required if mode of payment is `CREDIT`.')
    )
    pdf_file = models.FileField(
        upload_to='payments/receipts/',
        null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Payment transaction created date and time.')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Payment transaction last updated date and time.')
    )

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ('-created_at', )

    def __str__(self):
        return self.order.customer.name
    
    @cached_property
    def taxes(self):
        """
        Returns the TAX name, percentage, and tax amount of a Business Account
        """
        return self.order.taxes
    
    @cached_property
    def tax_percentage(self):
        """
        Returns the sum of all TAX percentages that are applied.
        """
        return self.order.tax_percentage

    @cached_property
    def tax_amount(self) -> float:
        """
        Returns the VAT Tax amount based order's cost.
        """
        return self.order.tax_amount

    @cached_property
    def order_amount(self):
        """
        Returns a total order amount for the payment *before* tax.
        """
        if self.order.order_type == Order.FROM_LIST and self.status == Payment.COMPLETED:
            total = sum(item.amount for item in self.sold_items.all())
            return round(total, 2)
        return self.order.cost

    @cached_property
    def total_amount(self):
        """
        Returns a total order amount for the payment *after* tax.
        """
        return round(self.order_amount + self.tax_amount, 2)

    def generate_pdf(self, request):
        """Generate a PDF file of the order."""
        template = get_template('payments/receipts/placeholder.html')
        context = {'payment': self}
        html = template.render(context)
        pdf_file = HTML(
            string=html,
            base_url=request.build_absolute_uri()
        ).write_pdf()
        self.pdf_file.save('receipt.pdf', ContentFile(pdf_file), save=True)


class SoldItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='sold_items'
    )
    product = models.TextField()
    unit = models.CharField(
        max_length=3,
        choices=MeasurementUnit.UNIT_CHOICES,
        default=MeasurementUnit.PIECE,
        help_text=_('Measurement unit.')
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _('Sold Item')
        verbose_name_plural = _('Sold Items')

    def __str__(self):
        return self.product

    @cached_property
    def amount(self) -> float:
        """
        Sub-total amount of the order item.
        """
        return round(self.quantity * self.price, 2)
