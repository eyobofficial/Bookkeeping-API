from django.contrib import admin

from .models import Stock


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
