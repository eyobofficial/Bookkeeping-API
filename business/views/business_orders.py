from django.utils.decorators import method_decorator
from rest_framework import permissions
from rest_framework.generics import get_object_or_404, ListAPIView, \
    CreateAPIView
from drf_yasg.utils import swagger_auto_schema

from orders.models import Order, OrderItem
from business.serializers import BusinessAllOrdersSerialize, \
    BusinessInventoryOrdersSerializer, BusinessCustomOrderSerializer
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='business-order-list',
        tags=['Orders'],
        responses={
            200: BusinessAllOrdersSerialize(many=True),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
        }
    )
)
class OrderListView(BaseBusinessAccountDetailViewSet, ListAPIView):
    """
    get:
    Business Order List

    Returns a list of all outstanding customer orders for a
    business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/orders/`

    **Response Body** <br />
    - Order ID
    - Customer Object
    - Total Cost
    - Description
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessAllOrdersSerialize


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        operation_id='business-inventory-order-create',
        tags=['Orders'],
        responses={
            201: BusinessInventoryOrdersSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
        }
    )
)
class InventoryOrderCreateView(BaseBusinessAccountDetailViewSet, CreateAPIView):
    """
    post:
    Business Order From Inventory

    Creates a customer order for a business account using a
    list of items from the inventory.

    **HTTP Request** <br />
    `POST /business/{business_id}/orders/from-list/`

    **Request Body Parameters** <br />
    - Customer ID
    - Order Item Objects
    - Mode Of Payment
    - Pay Later Date (*If Mode of Payment is `CASH`*)

    **Response Body** <br />
    - Order ID
    - Customer ID
    - Total Cost
    - Order Item Objects
    - Mode of Payment
    - Pay Later Date
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessInventoryOrdersSerializer
    permission_classes = [permissions.IsAuthenticated]


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        operation_id='business-custom-order-create',
        tags=['Orders'],
        responses={
            201: BusinessCustomOrderSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
        }
    )
)
class CustomOrderCreateView(BaseBusinessAccountDetailViewSet, CreateAPIView):
    """
    post:
    Business Order Custom

    Creates a customer order for a business account using a custom
    user described order description.

    **HTTP Request** <br />
    `POST /business/{business_id}/orders/custom/`

    **Request Body Parameters** <br />
    - Customer ID
    - Description
    - Custom Cost
    - Mode of Payment
    - Pay Later Date (*If Mode of Payment is `CASH`*)

    **Response Body** <br />
    - Order ID
    - Customer ID
    - Description
    - Total Cost
    - Mode of Payment
    - Pay Later Date
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessCustomOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

