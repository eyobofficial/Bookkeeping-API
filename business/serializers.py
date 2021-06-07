from django.utils.translation import gettext_lazy as _

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


class BusinessAllOrdersSerialize(serializers.ModelSerializer):
    """
    Serializer class for the list view of all orders.
    """
    customer = BusinessCustomerSerializer(read_only=True)
    description = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'customer',
            'total_cost',
            'description',
            'created_at',
            'updated_at'
        )

    def get_description(self, obj):
        if obj.order_type == Order.FROM_LIST:
            qs = obj.order_items.all()
            return ', '.join(
                [f'{self._stringfy_num(i.quantity)} {i.item.product}' for i in qs]
            )
        return obj.description

    def _stringfy_num(self, num):
        """
        Convert a decimal number to a human readable format.

        Examples:
          * 3.00 -> 3
          * 4.50 -> 4.5
          * 9.99 -> 9.99
        """
        whole, fraction = str(num).split('.')
        if fraction.rstrip('0') == '':
            return whole
        return '.'.join([whole, fraction.rstrip('0')])


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity')

    def validate(self, validated_data):
        order_quantity = validated_data['quantity']
        total_quantity = validated_data['item'].quantity

        if order_quantity > total_quantity:
            raise serializers.ValidationError(_('Ordered quantity is more than the stock.'))
        return validated_data

    def to_representation(self, instance):
        return {
            'id': instance.pk,
            'product': instance.item.product,
            'quantity': instance.quantity,
            'unit': instance.item.unit,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }


class BaseOrderModelSerializer(serializers.ModelSerializer):
    """
    Base model serializer for orders with different types.

    This is necessary to share common logic (example: validation)
    in accordance to the DRY principle.
    """

    def validate(self, validated_data):
        mode_of_payment = validated_data['mode_of_payment']
        pay_later_date = validated_data.get('pay_later_date')

        if mode_of_payment == Order.CREDIT and not pay_later_date:
            raise serializers.ValidationError(_('Pay later date is required.'))
        elif mode_of_payment != Order.CREDIT:
            validated_data['pay_later_date'] = None

        return validated_data


class BusinessInventoryOrdersSerializer(BaseOrderModelSerializer):
    """
    Serializer class for an order with `from_list` order type value.
    """
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'customer',
            'total_cost',
            'order_items',
            'mode_of_payment',
            'pay_later_date',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('cost', )

    def create(self, validated_data):
        item_data = validated_data.pop('order_items')
        validated_data['order_type'] = Order.FROM_LIST
        order = Order.objects.create(**validated_data)
        for item_data in item_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        item_data = validated_data.pop('order_items')
        instance.customer = validated_data.get('customer', instance.customer)
        # TODO


class BusinessCustomOrderSerializer(BaseOrderModelSerializer):
    """
    Serializer class for creating orders with `custom` order_type value.
    """

    class Meta:
        model = Order
        fields = (
            'id',
            'description',
            'custom_cost',
            'mode_of_payment',
            'pay_later_date',
            'created_at',
            'updated_at'
        )
