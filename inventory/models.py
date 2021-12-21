from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from business.models import BusinessAccount
from shared.models import PhotoUpload

from .units import MeasurementUnit


User = get_user_model()


class Barcode(models.Model):
    MANUALLY = 1
    API = 2
    CSV = 3

    CREATED_STRATEGY_OPTIONS = (
        (MANUALLY, _('Manually via Django Admin')),
        (API, _('API Calls')),
        (CSV, _('Imported from a CSV file')),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    barcode_number = models.CharField(max_length=255, unique=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField(help_text='Short description about the product.', blank=True)
    product_photo = models.OneToOneField(PhotoUpload,
                                         on_delete=models.CASCADE,
                                         related_name='barcode_product_photo',
                                         null=True, blank=True,
                                         help_text=_('A foreign key to the Photo Upload object.'))
    barcode_photo = models.ImageField(upload_to='barcodes', blank=True, null=True)
    manufacturer_name = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    created_strategy = models.IntegerField(choices=CREATED_STRATEGY_OPTIONS, default=MANUALLY,
                                           help_text=_('The strategy used to create this record.'))
    business_account = models.ForeignKey(BusinessAccount,
                                         null=True, blank=True,
                                         on_delete=models.SET_NULL,
                                         related_name='barcodes')
    verified = models.BooleanField(default=False,
                                   help_text=('Verify the entered barcode matches with the number '
                                              'in the uploaded photo.'))
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   related_name='created_barcodes',
                                   on_delete=models.SET_NULL)
    verified_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   related_name='verified_barcodes',
                                   on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.barcode_number


class Stock(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    product = models.CharField(_('product name'), max_length=100)
    unit = models.CharField(
        max_length=3,
        choices=MeasurementUnit.UNIT_CHOICES,
        help_text=_('Measurement unit.')
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text=_('Quantity left.')
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    photo = models.OneToOneField(
        PhotoUpload,
        on_delete=models.CASCADE,
        related_name='stock_photo',
        null=True, blank=True
    )
    barcode_number = models.CharField(max_length=255,
                                      null=True, blank=True,
                                      unique=True, default=None)
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
    quantity = models.DecimalField(_('quantity sold'),
        max_digits=12, decimal_places=2, default=0
    )
    sales_date = models.DateField(
        auto_now=True,
        help_text=_('last sales date')
    )

    class Meta:
        verbose_name = _('Product Sold')
        verbose_name_plural = _('Products Sold')

    def __str__(self):
        return self.stock.product
