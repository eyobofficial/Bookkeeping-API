from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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


class CustomerSerializer(serializers.ModelSerializer):
    """
    Customer serializer to include include in order serializer
    """

    class Meta:
        model = Customer
        fields = ('id', 'name', 'phone_number', 'email', 'photo')


class BusinessAllOrdersSerialize(serializers.ModelSerializer):
    """
    Serializer class for the list view of all orders.
    """
    customer = CustomerSerializer(read_only=True)
    description = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_type',
            'customer',
            'cost',
            'description',
            'mode_of_payment',
            'pay_later_date',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('order_type', )

    def get_cost(self, obj) -> float:
        return obj.cost

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

    def validate_pay_later_date(self, value):
        # Do not allow past dates
        now = timezone.now()
        if value < now.date():
            raise serializers.ValidationError(_('Date cannot be in the past.'))
        return value

    def validate(self, validated_data):
        mode_of_payment = validated_data['mode_of_payment']
        pay_later_date = validated_data.get('pay_later_date')

        # Make `pay_later_date` required is mode of payment is `CREDIT`
        if mode_of_payment == Order.CREDIT and not pay_later_date:
            error = {'pay_later_field': _('This field is required.')}
            raise serializers.ValidationError(error)
        return validated_data

    def to_internal_value(self, data):
        fields = super().to_internal_value(data)

        # If mode of payment is not credit, don't set `pay_later_date`
        if data['mode_of_payment'] != Order.CREDIT:
            fields.pop('pay_later_date', None)
        return fields

    def to_representation(self, instance):
        fields = super().to_representation(instance)

        # Include customer object serializered data
        customer_serializer = CustomerSerializer(instance.customer)
        fields['customer'] = customer_serializer.data

        # Include `pay_later_date` if only mode of payment is credit.
        if fields['mode_of_payment'] != Order.CREDIT:
            fields.pop('pay_later_date', None)
        return fields


class BusinessInventoryOrdersSerializer(BaseOrderModelSerializer):
    """
    Serializer class for an order with `from_list` order type value.
    """
    order_items = OrderItemSerializer(many=True)
    cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_type',
            'customer',
            'cost',
            'order_items',
            'mode_of_payment',
            'pay_later_date',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('cost', 'order_type')

    def get_cost(self, obj) -> float:
        # Necessary for `drf-yasg` to figure out the type.
        return obj.cost

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
    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'order_type',
            'customer',
            'description',
            'cost',
            'mode_of_payment',
            'pay_later_date',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('order_type', )

    def create(self, validated_data):
        # Set the cost to the `custom_cost` field instead
        validated_data['custom_cost'] = validated_data.pop('cost')
        validated_data['order_type'] = Order.CUSTOM
        order = Order.objects.create(**validated_data)
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    A *Read-Only serializer* for a customer order of all type.

    This is necessary to have a uniform response object for all order
    types (i.e. `FROM_LIST` and `CUSTOM`).
    """
    customer = CustomerSerializer()
    order_items = OrderItemSerializer(many=True)
    cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_type', 'customer', 'description',
            'order_items', 'cost', 'mode_of_payment',
            'pay_later_date', 'created_at', 'updated_at'
        )

    def get_cost(self, obj) -> float:
        # Required for `drf-yasg` to return the right type
        return obj.cost
