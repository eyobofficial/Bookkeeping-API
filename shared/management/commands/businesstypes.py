"""
Django management command to populate business types objects.

This script is used (as opposed to a simple fixture) in order to overwrite
existing icon images of the business type. If a record already exists in
the database, the script doesn't modify the title of the a record. For that,
the Django admin dashboard should be used.
"""
from django.core.management import BaseCommand

from business.models import BusinessType


class Command(BaseCommand):
    help = 'Populate business types objects.'

    def handle(self, *args, **kwargs):
        business_types = [
            {'id': 1, 'defaults': {'title': 'Online Store'}},
            {'id': 2, 'defaults': {'title': 'Fashion, Healthy & Beauty'}},
            {'id': 3, 'defaults': {'title': 'Cafe & Restaurants'}},
            {'id': 4, 'defaults': {'title': 'Food & Drink'}},
            {'id': 5, 'defaults': {'title': 'Gifts & Toys'}},
            {'id': 6, 'defaults': {'title': 'Home & Lifestyle'}},
            {'id': 7, 'defaults': {'title': 'Service & Consulting'}},
            {'id': 8, 'defaults': {'title': 'Autoshop & Repairs'}},
            {'id': 9, 'defaults': {'title': 'Supermarket & Convenience store'}},
            {'id': 10, 'defaults': {'title': 'Others'}},
        ]

        for business_type in business_types:
            obj, created = BusinessType.objects.get_or_create(**business_type)

            if created:
                self.stdout.write(f'{obj.title} business type is created.')
