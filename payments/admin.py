from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'mode_of_payment', 'amount', 'status', 'created_at')
    list_filter = ('mode_of_payment', 'status')
