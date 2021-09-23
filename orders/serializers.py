from rest_framework import serializers

from .models import OrderItem


class InventoryOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity', 'updated_at')
        extra_kwargs = {
            'order': {'help_text': 'ID of the Order.'},
            'item': {'help_text': 'ID of the product item from the inventory.'}
        }
