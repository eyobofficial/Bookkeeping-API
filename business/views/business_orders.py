from django.http import HttpResponse
from django.utils.decorators import method_decorator
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView, ListAPIView, \
    CreateAPIView, UpdateAPIView
from drf_yasg.utils import swagger_auto_schema

from orders.models import Order
from business.serializers import BusinessAllOrdersSerialize, \
    BusinessInventoryOrdersSerializer, BusinessCustomOrderSerializer, \
    OrderDetailSerializer
from business.permissions import IsAdminOrBusinessOwner, IsBusinessOwnedResource
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
    Customer Order List

    Returns a list of all outstanding customer orders for a
    business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/orders/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Query Parameters** <br />
    - `modeOfPayment`: Filter the customer orders of a business account by
      the their mode of payments. The possible value are: `CASH`, `BANK`,
      `CARD`, and `CREDIT`.

    **Response Body** <br />
    - Order ID
    - Order Type
    - Customer Object
    - Cost
    - Description
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessAllOrdersSerialize
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        mode_of_payment = self.request.query_params.get('modeOfPayment')
        if mode_of_payment is not None:
            qs = qs.filter(mode_of_payment=mode_of_payment)
        return qs


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='business-order-detail',
        tags=['Orders'],
        responses={
            200: OrderDetailSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
        }
    )
)
class OrderDetailView(BaseBusinessAccountDetailViewSet, RetrieveAPIView):
    """
    get:
    Customer Order Detail

    Returns a detail of an outstanding customer orders for a
    business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/orders/{order_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `order_id`: The ID of a customer order.

    **Response Body** <br />
    - Order ID
    - Order Type
    - Customer Object
    - Description (*`Null` for orders with `FROM_LIST` order types.*)
    - Order Item Objects (*Empty for orders with `CUSTOM` order types.*)
    - Cost
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = OrderDetailSerializer
    permission_classes = [IsBusinessOwnedResource]


class InventoryOrderCreateView(BaseBusinessAccountDetailViewSet, CreateAPIView):
    """
    post:
    Inventory Customer Order

    Creates a customer order for a business account using a
    list of items from the inventory.

    **HTTP Request** <br />
    `POST /business/{business_id}/orders/from-list/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Request Body Parameters** <br />
    - Customer ID
    - Order Item Objects
    - Mode Of Payment
    - Pay Later Date (*If Mode of Payment is `CREDIT`*)

    **Response Body** <br />
    - Order ID
    - Order Type (*Always `FROM_LIST`*)
    - Customer Object
    - Cost
    - Order Item Objects
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time

    **Validation Error Events** <br />
    - `customerId`, `orderItems`, and `modeOfPayments` are all required.
    - `payLaterDate` field is required if `modeOfPayment` has a
      value of `CREDIT`.
    - `quantity` of each `orderItems` cannot be more than what is available in
      the inventory.
    - `payLaterDate` cannot be date in the past.
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessInventoryOrdersSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='business-inventory-order-create',
        tags=['Orders'],
        responses={
            201: BusinessInventoryOrdersSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class InventoryOrderUpdateView(BaseBusinessAccountDetailViewSet, UpdateAPIView):
    """
    put:
    Inventory Customer Order Update

    Updates a customer order for a business account that that an order type
    of `FROM_LIST`.

    **HTTP Request** <br />
    `PUT /business/{business_id}/orders/{order_id}/from-list/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `order_id`: The ID of the customer order.

    **Request Body Parameters** <br />
    - Customer ID
    - Order Item Objects
    - Mode Of Payment
    - Pay Later Date (*If Mode of Payment is `CREDIT`*)

    **Response Body** <br />
    - Order ID
    - Order Type (*Always `FROM_LIST`*)
    - Customer Object
    - Cost
    - Order Item Objects
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time

    **Validation Error Events** <br />
    - `customerId`, `orderItems`, and `modeOfPayments` are all required.
    - `payLaterDate` field is required if `modeOfPayment` has a
      value of `CREDIT`.
    - `quantity` of each `orderItems` cannot be more than what is available in
      the inventory.
    - `payLaterDate` cannot be date in the past.

    patch:
    Inventory Order Partial Update

    Partially updates a customer order for a business account that that an
    order type of `FROM_LIST`.

    **HTTP Request** <br />
    `PATCH /business/{business_id}/orders/{order_id}/from-list/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `order_id`: The ID of the customer order.

    **Request Body Parameters** <br />
    - Customer ID
    - Order Item Objects
    - Mode Of Payment
    - Pay Later Date (*If Mode of Payment is `CREDIT`*)

    **Response Body** <br />
    - Order ID
    - Order Type (*Always `FROM_LIST`*)
    - Customer Object
    - Cost
    - Order Item Objects
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time

    **Validation Error Events** <br />
    - `customerId`, `orderItems`, and `modeOfPayments` are all required.
    - `payLaterDate` field is required if `modeOfPayment` has a
      value of `CREDIT`.
    - `quantity` of each `orderItems` cannot be more than what is available in
      the inventory.
    - `payLaterDate` cannot be date in the past.
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessInventoryOrdersSerializer
    permission_classes = [IsBusinessOwnedResource]

    @swagger_auto_schema(
        operation_id='business-inventory-order-update',
        tags=['Orders'],
        responses={
            200: BusinessInventoryOrdersSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
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
            404: 'Business Account Not Found',
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

    **HTTP Request** <br />
    `POST /business/{business_id}/orders/custom/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Request Body Parameters** <br />
    - Customer ID
    - Description
    - Cost
    - Mode of Payment
    - Pay Later Date (*If Mode of Payment is `CREDIT`*)

    **Response Body** <br />
    - Order Object
    - Order Type (*Always `CUSTOM`*)
    - Customer Object
    - Description
    - Cost
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time

    **Validation Error Events** <br />
    - `customerId`, `description`, `cost`, and `modeOfPayments` are
      all required.
    - `payLaterDate` field is required if `modeOfPayment` has a
      value of `CREDIT`.
    - `payLaterDate` cannot be date in the past.
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessCustomOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='business-custom-order-create',
        tags=['Orders'],
        responses={
            201: BusinessCustomOrderSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomOrderUpdateView(BaseBusinessAccountDetailViewSet, UpdateAPIView):
    """
    put:
    Custom Order Update

    Updates a customer order for a business account that that an order type
    of `CUSTOM`.

    **HTTP Request** <br />
    `PUT /business/{business_id}/orders/{order_id}/custom/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `order_id`: The ID of the customer order.

    **Request Body Parameters** <br />
    - Customer ID
    - Description
    - Cost
    - Mode of Payment
    - Pay Later Date (*If Mode of Payment is `CREDIT`*)

    **Response Body** <br />
    - Order Object
    - Order Type (*Always `CUSTOM`*)
    - Customer Object
    - Description
    - Cost
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time

    **Validation Error Events** <br />
    - `customerId`, `description`, `cost`, and `modeOfPayments` are
      all required.
    - `payLaterDate` field is required if `modeOfPayment` has a
      value of `CREDIT`.
    - `payLaterDate` cannot be date in the past.

    patch:
    Custom Order Partial Update

    Partial updates a customer order for a business account that
    that an order type of `CUSTOM`.

    **HTTP Request** <br />
    `PATCH /business/{business_id}/orders/{order_id}/custom/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `order_id`: The ID of the customer order.

    **Request Body Parameters** <br />
    - Customer ID
    - Description
    - Cost
    - Mode of Payment
    - Pay Later Date (*If Mode of Payment is `CREDIT`*)

    **Response Body** <br />
    - Order Object
    - Order Type (*Always `CUSTOM`*)
    - Customer Object
    - Description
    - Cost
    - Mode of Payment
    - Pay Later Date (*Null for orders with mode of payment other than `CREDIT`*)
    - Create Date & Time
    - Last Updated Date & Time

    **Validation Error Events** <br />
    - `customerId`, `description`, `cost`, and `modeOfPayments` are
      all required.
    - `payLaterDate` field is required if `modeOfPayment` has a
      value of `CREDIT`.
    - `payLaterDate` cannot be date in the past.
    """
    queryset = Order.objects.filter(is_completed=False)
    serializer_class = BusinessCustomOrderSerializer
    permission_classes = [IsBusinessOwnedResource]

    @swagger_auto_schema(
        operation_id='business-custom-order-update',
        tags=['Orders'],
        responses={
            200: BusinessCustomOrderSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Business Account Not Found',
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
            404: 'Business Account Not Found',
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='customer-order-download',
        tags=['Orders'],
        responses={
            200: 'A PDF Download URL',
            401: 'Unauthorized',
            404: 'Not Found',
        }
    )
)
class OrderPdfDownloadView(BaseBusinessAccountDetailViewSet, RetrieveAPIView):
    """
    get:
    Cutomer Order Receipt

    Returns a URL to PDF receipt file for the custom order.

    **HTTP Request** <br />
    `GET /business/{business_id}/orders/{order_id}/download/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `order_id`: The ID of the customer order.

    **Response Body** <br />
    A URL to the PDF receipt download link.
    """
    queryset = Order.objects.all()
    permission_classes = [IsBusinessOwnedResource]

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        order.generate_pdf(request)
        response = HttpResponse(order.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Receipt.pdf"'
        return response
