from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField


User = settings.AUTH_USER_MODEL


class BusinessType(models.Model):
    """
    Business categories.
    """
    title = models.CharField(max_length=100)
    icon = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = _('Business Type')
        verbose_name_plural = _('Business Types')
        ordering = ('id', )

    def __str__(self):
        return self.title


def get_default_business_type():
    """
    Returns a default business types.
    """
    return BusinessType.objects.get_or_create(title__iexact='Others')[0]


class BusinessAccount(models.Model):
    """
    User business account model.
    """

    # Currency Choices
    USD = 'USD'   # US Dollar
    EURO = 'EUR'  # Euro
    GBP = 'GBP'  # Pound Streling
    NGN = 'NGN'  # Nigerian Naira

    CURRENCY_CHOICES = (
        (USD, _('US Dollar')),
        (EURO, _('Euro')),
        (GBP, _('Pound Sterling')),
        (NGN, _('Nigerian Naira')),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(_('business name'), max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_type = models.ForeignKey(
        BusinessType,
        on_delete=models.SET(get_default_business_type)
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=NGN
    )
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField()
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Business Account')
        verbose_name_plural = _('Business Accounts')
        default_related_name = 'business_accounts'

    def __str__(self):
        return self.name


class BusinessAccountTax(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    business_account = models.ForeignKey(
        BusinessAccount,
        related_name='taxes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    tax_identification_number = models.CharField(
        max_length=100,
        null=True, blank=True,
        help_text=_('Unique TAX identification number issued by the government.'))
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_('The percentage to be deducted.')
    )
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Business Account Tax')
        verbose_name_plural = _('Business Account Taxes')

    def __str__(self):
        return self.name

    def get_tax_amount(self, amount):
        """
        Given an amount to be taxed, returns the tax amount.
        """
        return round((amount * self.percentage) / 100, 2)
