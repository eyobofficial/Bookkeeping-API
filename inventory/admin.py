from django.contrib import admin

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


@admin.register(Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('barcode_number', 'product_name', 'verified', 'archived')
    list_display_links = ('barcode_number', 'product_name')
    list_editable = ('verified', 'archived')
    list_filter = ('verified', 'archived', 'created_at')
    search_fields = ('code', 'product_name', 'description')
