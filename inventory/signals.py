from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Stock, Sold


@receiver(post_save, sender=Stock)
def create_sold_record(sender, instance, created, **kwargs):
    """
    Create a `Sold` instance for each stock instance.
    """
    if created:
        Sold.objects.create(stock=instance)
