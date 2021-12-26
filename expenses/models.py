from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from business.models import BusinessAccount


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    business_account = models.ForeignKey(BusinessAccount,
                                         on_delete=models.CASCADE,
                                         related_name='expenses')
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ('-created_at', )

    def __str__(self):
        return self.title
