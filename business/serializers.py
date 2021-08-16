from decimal import Decimal
from functools import reduce

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin
from drf_yasg.utils import swagger_serializer_method

from customers.models import Customer
from expenses.models import Expense
from inventory.models import Stock, Sold
from orders.models import Order, OrderItem
from payments.models import Payment, SoldItem
from notifications.models import Notification
from shared.fields import PhotoUploadField
from shared.models import PhotoUpload

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
    photo = PhotoUploadField(required=False, allow_null=True)

    class Meta:
        model = Customer
        fields = (
            'id', 'name', 'phone_number', 'email',
            'photo', 'created_at', 'updated_at'
        )

    def update(self, instance, valiated_data):
        photo_data = valiated_data.pop('photo', None)
        if photo_data is None:
            instance.photo = None
        else:
            instance.photo = self._get_photo(photo_data)
        return super().update(instance, valiated_data)

    def create(self, validated_data):
        photo_data = validated_data.pop('photo', None)
        if photo_data is not None:
            validated_data['photo'] = self._get_photo(photo_data)
        return super().create(validated_data)

    def _get_photo(self, photo_data):
        """
        Get customer photo from unploaded photo instance.

        params:
          photo_data (dict): The serialized dictonary of the PhotoUploaded
          instance.
        """
        photo_id = photo_data['id']
        return PhotoUpload.objects.get(pk=photo_id)


class BusinessExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = ('id', 'title', 'amount', 'date', 'created_at')


class BusinessStockSerializer(serializers.ModelSerializer):
    photo = PhotoUploadField(required=False, allow_null=True)

    class Meta:
        model = Stock
        fields = (
            'id', 'product', 'unit', 'quantity', 'price',
            'photo', 'created_at', 'updated_at'
        )

    def update(self, instance, valiated_data):
        photo_data = valiated_data.pop('photo', None)
        if photo_data is None:  # i.e. either photo is `null` or missing
            instance.photo = None
        else:
            instance.photo = self._get_photo(photo_data)
        return super().update(instance, valiated_data)

    def create(self, validated_data):
        photo_data = validated_data.pop('photo', None)
        if photo_data is not None:
            validated_data['photo'] = self._get_photo(photo_data)
        return super().create(validated_data)

    def _get_photo(self, photo_data):
        """
        Get inventory stock photo from unploaded photo instance.

        params:
          photo_data (dict): The serialized dictonary of the PhotoUploaded
          instance.
        """
        photo_id = photo_data['id']
        return PhotoUpload.objects.get(pk=photo_id)


class BusinessSoldSerializer(serializers.ModelSerializer):
    """
    Inventory sold serializer class.
    """
    product = serializers.ReadOnlyField(source='stock.product')
    unit = serializers.ReadOnlyField(source='stock.unit')
    price = serializers.DecimalField(
        read_only=True, source='stock.price',
        max_digits=10, decimal_places=2
    )

    class Meta:
        model = Sold
        fields = (
            'id', 'product', 'unit', 'quantity',
            'price', 'sales_date'
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
    cost = serializers.SerializerMethodField()
    tax_percentage = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_type',
            'customer',
            'cost',
            'tax_percentage',
            'tax_amount',
            'total_amount',
            'description',
            'status',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('order_type', )

    def get_cost(self, obj) -> float:
        return obj.cost

    def get_tax_percentage(self, obj) -> float:
        """
        Returns the TAX percentage in decimals.
        """
        return settings.VAT

    def get_tax_amount(self, obj) -> float:
        """
        Returns the TAX amount to be deducted.
        """
        tax_percentage = self.get_tax_percentage(obj)
        return round(obj.cost * tax_percentage, 2)

    def get_total_amount(self, obj) -> float:
        """
        Returns total amount to be after TAX.
        """
        tax_amount = self.get_tax_amount(obj)
        return round(tax_amount + obj.cost, 2)


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity', 'price', 'cost')
        validators = []

    def validate(self, validated_data):
        order_quantity = validated_data['quantity']
        total_quantity = validated_data['item'].quantity
        if order_quantity > total_quantity:
            error = {'quantity': _('Ordered quantity is more than the stock.')}
            raise serializers.ValidationError(error)
        return validated_data

    def to_representation(self, instance):
        return {
            'id': instance.pk,
            'product': instance.item.product,
            'quantity': instance.quantity,
            'unit': instance.item.unit,
            'price': instance.item.price,
            'cost': instance.cost,
            'updated_at': instance.updated_at
        }

    def get_price(self, obj) -> float:
        """
        Returns the item price per unit.
        """
        return obj.item.price

    def get_cost(self, obj) -> float:
        """
        Returns the subtotal cost of the item.
        """
        return obj.cost


class BaseOrderModelSerializer(serializers.ModelSerializer):
    """
    Base model serializer for orders with different types.

    This is necessary to share common logic (example: validation)
    in accordance to the DRY principle.
    """

    def to_representation(self, instance):
        fields = super().to_representation(instance)

        # Include customer object serializered data
        customer_serializer = CustomerSerializer(instance.customer)
        fields['customer'] = customer_serializer.data
        return fields


class BusinessInventoryOrdersSerializer(BaseOrderModelSerializer):
    """
    Serializer class for an order with `from_list` order type value.
    """
    order_items = OrderItemSerializer(many=True)
    cost = serializers.SerializerMethodField()
    tax_percentage = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_type',
            'customer',
            'cost',
            'tax_percentage',
            'tax_amount',
            'total_amount',
            'description',
            'status',
            'order_items',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('cost', 'order_type')

    def get_cost(self, obj) -> float:
        # Necessary for `drf-yasg` to figure out the type.
        return obj.cost

    def get_tax_percentage(self, obj) -> float:
        """
        Returns the TAX percentage in decimals.
        """
        return settings.VAT

    def get_tax_amount(self, obj) -> float:
        """
        Returns the TAX amount to be deducted.
        """
        tax_percentage = self.get_tax_percentage(obj)
        return round(obj.cost * tax_percentage, 2)

    def get_total_amount(self, obj) -> float:
        """
        Returns total amount to be after TAX.
        """
        tax_amount = self.get_tax_amount(obj)
        return round(tax_amount + obj.cost, 2)

    def create(self, validated_data):
        item_data = validated_data.pop('order_items')
        validated_data['order_type'] = Order.FROM_LIST
        order = Order.objects.create(**validated_data)
        for item_data in item_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('order_items')
        instance.customer = validated_data.get('customer', instance.customer)
        instance.save()
        instance.order_items.all().delete()
        for item_data in items_data:
            instance.order_items.create(**item_data)
        return instance


class BusinessCustomOrderSerializer(BaseOrderModelSerializer):
    """
    Serializer class for creating orders with `custom` order_type value.
    """
    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )
    tax_percentage = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_type',
            'customer',
            'description',
            'status',
            'cost',
            'tax_percentage',
            'tax_amount',
            'total_amount',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('order_type', 'status')

    def get_tax_percentage(self, obj) -> float:
        """
        Returns the TAX percentage in decimals.
        """
        return settings.VAT

    def get_tax_amount(self, obj) -> float:
        """
        Returns the TAX amount to be deducted.
        """
        tax_percentage = self.get_tax_percentage(obj)
        return round(obj.cost * tax_percentage, 2)

    def get_total_amount(self, obj) -> float:
        """
        Returns total amount to be after TAX.
        """
        tax_amount = self.get_tax_amount(obj)
        return round(tax_amount + obj.cost, 2)

    def create(self, validated_data):
        # Set the cost to the `custom_cost` field instead
        validated_data['custom_cost'] = validated_data.pop('cost')
        validated_data['order_type'] = Order.CUSTOM
        order = Order.objects.create(**validated_data)
        return order

    def update(self, instance, validated_data):
        instance.customer = validated_data.get('customer', instance.customer)
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        instance.custom_cost = validated_data.get('cost', instance.custom_cost)
        instance.save()
        return instance


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    A *Read-Only serializer* for a customer order of all type.

    This is necessary to have a uniform response object for all order
    types (i.e. `FROM_LIST` and `CUSTOM`).
    """
    customer = CustomerSerializer()
    order_items = OrderItemSerializer(many=True)
    cost = serializers.SerializerMethodField()
    tax_percentage = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_type', 'customer', 'description', 'status',
            'order_items', 'cost', 'tax_percentage', 'tax_amount',
            'total_amount', 'created_at', 'updated_at'
        )

    def cost(self, obj) -> float:
        # Required for `drf-yasg` to return the right type
        return obj.cost

    def get_tax_percentage(self, obj) -> float:
        """
        Returns the TAX percentage in decimals.
        """
        return settings.VAT

    def get_tax_amount(self, obj) -> float:
        """
        Returns the TAX amount to be deducted.
        """
        tax_percentage = self.get_tax_percentage(obj)
        return round(obj.cost * tax_percentage, 2)

    def get_total_amount(self, obj) -> float:
        """
        Returns total amount to be after TAX.
        """
        tax_amount = self.get_tax_amount(obj)
        return round(tax_amount + obj.cost, 2)


class SoldItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoldItem
        fields = ('product', 'unit', 'quantity', 'price', 'amount')


class PaymentSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    description = serializers.ReadOnlyField(source='order.description')
    order_amount = serializers.SerializerMethodField(
        help_text=_('Total amount of the order (i.e. before TAX).')
    )
    tax_percentage = serializers.SerializerMethodField(
        help_text=_('TAX Percentage in decimals.')
    )
    tax_amount = serializers.SerializerMethodField(
        help_text=_('TAX amount to be added.')
    )
    total_amount = serializers.SerializerMethodField(
        help_text=_('Total amount of the payment (i.e. after TAX).')
    )
    sold_items = SoldItemSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'customer', 'description', 'order_amount', 'sold_items',
            'tax_percentage', 'tax_amount', 'total_amount', 'status',
            'mode_of_payment', 'pay_later_date', 'created_at', 'updated_at'
        )

    @swagger_serializer_method(serializer_or_field=CustomerSerializer)
    def get_customer(self, obj):
        return CustomerSerializer(instance=obj.order.customer).data

    def get_tax_percentage(self, obj) -> Decimal:
        """
        Returns the tax percentage.
        """
        return settings.VAT

    def get_tax_amount(self, obj) -> Decimal:
        """
        Returns the VAT amount.
        """
        return obj.tax_amount

    def get_order_amount(self, obj) -> Decimal:
        """
        Returns the total order amount (i.e. before tax).
        """
        return obj.order_amount

    def get_total_amount(self, obj) -> float:
        """
        Returns the total payment amount (i.e. after tax).
        """
        return obj.total_amount

    def validate_pay_later_date(self, value):
        # Do not allow past dates
        now = timezone.now()
        if value and value < now.date():
            raise serializers.ValidationError(_('Date cannot be in the past.'))
        return value

    def to_internal_value(self, data):
        fields = super().to_internal_value(data)

        # If mode of payment is not credit, don't set `pay_later_date`
        mode_of_payment = data.get('mode_of_payment')
        if mode_of_payment != Payment.CREDIT:
            fields.pop('pay_later_date', None)
        return fields

    def create(self, *args, **kwargs):
        payment = super().create(*args, **kwargs)

        # Add sold items record
        if payment.order.order_type == Order.CUSTOM:
            kwargs = {
                'payment': payment,
                'product': payment.order.description,
                'quantity': 1,
                'price': payment.order.custom_cost,
            }
            SoldItem.objects.create(**kwargs)
        else:
            for order_item in payment.order.order_items.all():
                kwargs = {
                    'payment': payment,
                    'product': order_item.item.product,
                    'unit': order_item.item.unit,
                    'quantity': order_item.quantity,
                    'price': order_item.item.price
                }
                SoldItem.objects.create(**kwargs)
        return payment

    def save(self, *args, **kwargs):
        payment = super().save(*args, **kwargs)
        if payment.status == Payment.COMPLETED:
            # Deduct inventory and Sold
            order_items = payment.order.order_items.all()
            for order_item in order_items:
                order_item.item.sell(order_item.quantity)

            # Close order
            payment.order.status = Order.CLOSED
            payment.order.save()

        return payment


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for current business account notifications.
    """

    class Meta:
        model = Notification
        fields = (
            'id', 'notification_type', 'action_message', 'action_url',
            'action_date', 'action_date_label', 'is_seen', 'created_at',
            'updated_at'
        )
        read_only_fields = (
            'notification_type',
            'action_message',
            'action_url',
            'action_date',
            'action_date_label',
            'created_at',
            'updated_at'
        )
