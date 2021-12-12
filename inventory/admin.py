from django.contrib import admin

from import_export import resources
from import_export.admin import ImportMixin
from import_export.fields import Field
from import_export.formats.base_formats import CSV

from .models import Barcode, Stock, Sold


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'business_account',
        'unit',
        'quantity',
        'price',
        'barcode_number',
        'created_at',
        'updated_at'
    )
    search_fields = ('product', )


@admin.register(Sold)
class SoldAdmin(admin.ModelAdmin):
    list_display = (
        'get_business_account',
        'stock',
        'quantity',
        'sales_date'
    )
    list_display_links = ('get_business_account', 'stock')

    def get_business_account(self, obj):
        return obj.stock.business_account

    get_business_account.short_description = 'Business Account'


class BarcodeResource(resources.ModelResource):
    class Meta:
        model = Barcode
        import_id_fields = ('barcode_number', )
        fields = ('product_name', 'barcode_number', 'description', 'manufacturer_name')

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        instance.created_strategy = Barcode.CSV
        instance.verified = True
        super().save_instance(instance, using_transactions, dry_run)


@admin.register(Barcode)
class BarcodeAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ('barcode_number', 'product_name', 'verified', 'archived', 'created_strategy',
                    'created_at')
    readonly_fields = ('created_strategy', )
    list_filter = ('verified', 'archived', 'created_strategy')
    resource_class = BarcodeResource
    formats = [CSV]
