from rest_framework import serializers

from django_countries.serializers import CountryFieldMixin

from customers.models import Customer
from expenses.models import Expense
from inventory.models import Stock
from orders.models import Order, OrderItem

from .models import BusinessType, BusinessAccount


class BusinessTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessType
        fields = ('id', 'title', 'icon')


class BusinessAccountSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = BusinessAccount
        fields = '__all__'


class BusinessCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = (
            'id', 'name', 'phone_number', 'email',
            'photo', 'created_at', 'updated_at'
        )
        read_only_fields = ('photo', 'created_at', 'updated_at')


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


class BusinessOrderSerialize(serializers.ModelSerializer):
    customer = BusinessCustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'customer',
            'cost',
            'created_at',
            'updated_at'
        )
