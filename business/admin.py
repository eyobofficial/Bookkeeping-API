from django.contrib import admin

from customers.models import Customer

from .models import BusinessType, BusinessAccount


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


class CustomerInline(admin.TabularInline):
    model = Customer
    extra = 1


@admin.register(BusinessAccount)
class BusinessAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'business_type', 'created_at', 'updated_at')
    list_filter = ('business_type', )
    search_fields = ('business_name', )
    inlines = [CustomerInline]
