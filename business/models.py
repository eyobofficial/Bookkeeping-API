from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


User = settings.AUTH_USER_MODEL


class BusinessType(models.Model):
    """
    Business categories.
    """
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('Business Type')
        verbose_name_plural = _('Business Types')
        ordering = ('id', 'title', )

    def __str__(self):
        return self.title


# class BusinessAccount(models.Model):
#     """
#     User business account model.
#     """
#     id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='business_accounts'
#     )
#     category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE)

