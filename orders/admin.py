from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'business_account',
        'order_type',
        'cost',
        'mode_of_payment',
        'created_at',
        'updated_at'
    )
    list_editable = ('order_type', 'mode_of_payment')
    list_filter = ('order_type', )
    inlines = [OrderItemInline]
