from django.contrib import admin

from .models import Payment, SoldItem


class SoldItemInline(admin.TabularInline):
    model = SoldItem
    extra = 1


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'mode_of_payment', 'order_amount',
        'total_tax_amount', 'total_amount', 'status', 'created_at'
    )
    list_filter = ('mode_of_payment', 'status')
    inlines = [SoldItemInline]
