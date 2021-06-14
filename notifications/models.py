from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from business.models import BusinessAccount


class Notification(models.Model):
    """
    Notifications directed to a business account.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    notification_type = models.CharField(
        max_length=255,
        help_text=_('Category or the notication.')
    )
    business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    action_message = models.TextField()
    action_url = models.URLField(
        blank=True, null=True,
        help_text=_('URL for the action resource.')
    )
    action_date = models.DateTimeField(
        blank=True, null=True,
        help_text=_('Date and time for taking the action.')
    )
    action_date_label = models.CharField(
        max_length=255,
        help_text=_('Label to display for the action date.'),
        default='Date & time'
    )
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ('is_seen', '-created_at')

    def __str__(self):
        return self.action_message
