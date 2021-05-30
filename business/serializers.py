from rest_framework import serializers

from django_countries.serializers import CountryFieldMixin

from customers.models import Customer
from expenses.models import Expense
from inventory.models import Stock

from .models import BusinessType, BusinessAccount


class BusinessTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessType
        fields = ('id', 'title', 'icon')


class BusinessAccountSerializer(CountryFieldMixin, serializers.ModelSerializer):
    business_type = BusinessTypeSerializer(read_only=True)

    class Meta:
        model = BusinessAccount
        fields = '__all__'


class BusinessCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = (
            'id', 'name', 'phone_number',
            'email', 'created_at', 'updated_at'
        )


class BusinessExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = ('id', 'title', 'amount', 'date', 'created_at')


class BusinessStockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = (
            'id', 'product', 'unit', 'quantity',
            'price', 'created_at', 'updated_at'
        )
