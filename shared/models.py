from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class PhotoUpload(models.Model):
    """
    User uploaded profile photo.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    photo = models.ImageField(upload_to='profiles', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Photo Upload')
        verbose_name_plural = _('Photo Uploads')
        ordering = ('-created_at', )

    def __str__(self):
        return str(self.id)
