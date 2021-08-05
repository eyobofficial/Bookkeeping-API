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
        'get_business_account',
        'stock',
        'quantity',
        'sales_date'
    )
    list_display_links = ('get_business_account', 'stock')

    def get_business_account(self, obj):
        return obj.stock.business_account

    get_business_account.short_description = 'Business Account'
