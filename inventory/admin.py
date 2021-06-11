from django.contrib import admin

from .models import Stock, Sold


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'business_account',
        'unit',
        'quantity',
        'price',
        'created_at',
        'updated_at'
    )
    search_fields = ('product', )


@admin.register(Sold)
class SoldAdmin(admin.ModelAdmin):
    list_display = (
        'stock',
        'quantity',
        'sales_date'
    )
