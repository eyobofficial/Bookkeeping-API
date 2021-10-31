from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import permissions
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView,\
    RetrieveDestroyAPIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters import rest_framework as filters

from business import schema as business_schema
from orders.models import Order
from business.serializers import BusinessAllOrdersSerialize, \
    BusinessInventoryOrdersSerializer, BusinessCustomOrderSerializer, \
    OrderDetailSerializer
from business.permissions import IsBusinessOwnedResource, IsOrderOpen
from orders.filters import OrderFilter
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='business-order-list',
        tags=['Orders'],
        manual_parameters=[
            openapi.Parameter(
                'customer',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_(('Filter result by all or part of the '
                               'customer name, phone number, or email.')),
            ),
            openapi.Parameter(
                'type',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by the type of the order.'),
                enum=('from_list', 'custom')
            ),
            openapi.Parameter(
                'status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by the status of an order.'),
                enum=('open', 'closed')
            ),
            openapi.Parameter(
                'date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_(
                    'Filter result by the date of the order. Date format: `yyyy-mm-dd`.'
                )
            ),
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_(('Filter result by customer name, customer phone number, '
                               'customer email, order description, or order created date. '
                               'For searching by date, use the format `yyyy-mm-dd`.')),
            ),
        ],
        responses={
            200: BusinessAllOrdersSerialize(many=True),
            # 200: business_schema.order_list_response_body,
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Not Found',
        }
    )
)
class OrderListView(BaseBusinessAccountDetailViewSet, ListAPIView):
    """
    get:
    Customer Order List

    Returns a list of all (both open and closed) customer orders for a
    business account.
    """
    queryset = Order.objects.all()
    serializer_class = BusinessAllOrdersSerialize
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrderFilter


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='business-order-detail',
        tags=['Orders'],
        responses={
            200: OrderDetailSerializer,
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Not Found',
        }
    )
)
@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        operation_id='business-order-delete',
        tags=['Orders'],
        responses={
            204: 'No Content',
            401: 'Unauthorized',
            403: 'Updating or deleting closed order is not allowed.',
            404: 'Not Found',
        }
    )
)
class OrderDetailView(BaseBusinessAccountDetailViewSet, RetrieveDestroyAPIView):
    """
    get:
    Customer Order Detail

    Returns a detail of an outstanding customer orders for a
    business account.

    delete:
    Custom Order Delete

    Delete a customer order for a business account.
    """
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsBusinessOwnedResource]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes += [IsOrderOpen]
        return [permission() for permission in self.permission_classes]


class InventoryOrderCreateView(BaseBusinessAccountDetailViewSet, CreateAPIView):
    """
    post:
    Inventory Customer Order

    Creates a customer order for a business account using a
    list of items from the inventory.

    **Validation Error Events** <br />
    - `customerId` and `orderItems` are all required.
    - `quantity` of each `orderItems` cannot be more than what is available in
      the inventory.
    """
    queryset = Order.objects.all()
    serializer_class = BusinessInventoryOrdersSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='business-inventory-order-create',
        tags=['Orders'],
        responses={
            201: BusinessInventoryOrdersSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Not Found',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class InventoryOrderUpdateView(BaseBusinessAccountDetailViewSet, UpdateAPIView):
    """
    put:
    Inventory Customer Order Update

    Updates a customer order for a business account that has an order type
    of `FROM_LIST`.

    **Validation Error Events** <br />
    - `customerId` and `orderItems` are all required.
    - `quantity` of each `orderItems` cannot be more than what is available in
      the inventory.

    patch:
    Inventory Order Partial Update

    Partially updates a customer order for a business account that that an
    order type of `FROM_LIST`.

    **Validation Error Events** <br />
    - `customerId` and `orderItems` are all required.
    - `quantity` of each `orderItems` cannot be more than what is available in
      the inventory.
    """
    queryset = Order.objects.all()
    serializer_class = BusinessInventoryOrdersSerializer
    permission_classes = [IsBusinessOwnedResource, IsOrderOpen]

    @swagger_auto_schema(
        operation_id='business-inventory-order-update',
        tags=['Orders'],
        responses={
            200: BusinessInventoryOrdersSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            403: 'Updating or Deleting closed order is not allowed.',
            404: 'Not Found',
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='business-inventory-order-partial-update',
        tags=['Orders'],
        responses={
            200: BusinessInventoryOrdersSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            403: 'Updating or Deleting closed order is not allowed.',
            404: 'Not Found',
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CustomOrderCreateView(BaseBusinessAccountDetailViewSet, CreateAPIView):
    """
    post:
    Custom Customer Order

    Creates a customer order for a business account using a custom
    user described order description.

    **Validation Error Events** <br />
    - `customerId`, `description`, and `cost` are all required.
    """
    queryset = Order.objects.all()
    serializer_class = BusinessCustomOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='business-custom-order-create',
        tags=['Orders'],
        responses={
            201: BusinessCustomOrderSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Not Found',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomOrderUpdateView(BaseBusinessAccountDetailViewSet, UpdateAPIView):
    """
    put:
    Custom Order Update

    Updates a customer order for a business account that has an order type
    of `CUSTOM`.

    **Validation Error Events** <br />
    - `customerId`, `description`, and `cost` are all required.

    patch:
    Custom Order Partial Update

    Partial updates a customer order for a business account that
    that an order type of `CUSTOM`.

    **Validation Error Events** <br />
    - `customerId`, `description`, and `cost` are all required.
    """
    queryset = Order.objects.all()
    serializer_class = BusinessCustomOrderSerializer
    permission_classes = [IsBusinessOwnedResource, IsOrderOpen]

    @swagger_auto_schema(
        operation_id='business-custom-order-update',
        tags=['Orders'],
        responses={
            200: BusinessCustomOrderSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            403: 'Updating or Deleting closed order is not allowed.',
            404: 'Not Found',
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='business-custom-order-partial-update',
        tags=['Orders'],
        responses={
            200: BusinessCustomOrderSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            403: 'Updating or Deleting closed order is not allowed.',
            404: 'Not Found',
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
