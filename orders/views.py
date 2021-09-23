from django.utils.decorators import method_decorator

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

from shared import schema as shared_schema
from .models import OrderItem
from .serializers import InventoryOrderItemSerializer



@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_id='order-item-create',
        tags=['Order Items'],
        responses={
            201: InventoryOrderItemSerializer,
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_id='order-item-list',
        tags=['Order Items'],
        responses={
            200: InventoryOrderItemSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_id='order-item-detail',
        tags=['Order Items'],
        responses={
            200: InventoryOrderItemSerializer,
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        operation_id='order-item-update',
        tags=['Order Items'],
        responses={
            200: InventoryOrderItemSerializer,
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_id='order-item-partial-update',
        tags=['Order Items'],
        responses={
            200: InventoryOrderItemSerializer,
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        operation_id='order-item-delete',
        tags=['Order Items'],
        responses={
            204: 'No Content',
            401: shared_schema.unauthorized_401_response
        }
    )
)
class OrderItemViewSet(viewsets.ModelViewSet):
    """
    create:
    Order Item Create

    Create a new order items that is associated with the current order id.

    list:
    Order Item List

    Returns a list of all order items that are associated with the current
    order id.

    retrieve:
    Order Item Detail

    Returns a single order item that is associated with the current order id.

    update:
    Order Item Update

    Update a single order item that is associated with the current order id.

    partial_update:
    Order Item Partial Update

    Partially update a single order item that is associated with the current order id.

    destroy:
    Order Item Delete

    Delete a single order item that is associated with the current order id.
    """
    queryset = OrderItem.objects.all()
    serializer_class = InventoryOrderItemSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        order_id = self.kwargs.get('order_id')
        return qs.filter(order__id=order_id)
