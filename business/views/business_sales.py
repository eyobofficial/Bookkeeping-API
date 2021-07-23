from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from payments.models import Payment
from business.serializers import PaymentSerializer
from business.permissions import IsBusinessOwnedPayment


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_id='business-sales-list',
        tags=['Sales'],
        manual_parameters=[
            openapi.Parameter(
                'modeOfPayment',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by the mode of payment.'),
                enum=('CASH', 'BANK', 'CARD', 'CREDIT')
            ),
            openapi.Parameter(
                'customer',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by customer name.')
            )
        ],
        responses={
            200: PaymentSerializer(many=True),
            401: 'Unauthorized'
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_id='business-sales-detail',
        tags=['Sales'],
        responses={
            200: PaymentSerializer(),
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
)
class SalesViewSet(ReadOnlyModelViewSet):
    """
    list:
    Sales List

    Returns a list (array) of all completed sales for the current business
    account. Completed sales are the same as payments objects with a status
    of `COMPLETED`.

    **HTTP Request** <br />
    `GET /business/{business_id}/sales/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Query Parameters** <br />
    - `modeOfPayment`: Filter sales of a business account by their
      mode of payments. The possible value are: `CASH`, `BANK`, `CARD`,
      and `CREDIT`.
    - `customer`: Filter sales of a business account by the customer name.

    **Response Body** <br />
    An array of a sales object which includes:
    - Payment/Sales ID
    - Order ID
    - Orders Description (i.e. Summary of sold items)
    - Customer Object
    - Order Amount (Before TAX)
    - Tax Percentage (example: `0.15` for 15%)
    - Tax Amount
    - Total Amount (After Tax)
    - Mode of Payment
    - Pay Later Date (*Optional*)
    - An array of Sold Items Object. Object fields are:
        * Product
        * Unit
        * Quantity
        * Price
        * Amount
    - Status (Available values are `PENDING`, `COMPLETED`, and `FAILED`)
    - Create Date & Time
    - Last Updated Date & Time

    retrieve:
    Sales Detail

    Returns a detail of completed sales instance for the current business
    account. Completed sales are the same as payments objects with a status
    of `COMPLETED`.

    **HTTP Request** <br />
    `GET /business/{business_id}/sales/{sales_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `sales_id`: The ID of the sales object.

    **Response Body** <br />
    - Payment/Sales ID
    - Order ID
    - Orders Description (i.e. Summary of sold items)
    - Customer Object
    - Order Amount (Before TAX)
    - Tax Percentage (example: `0.15` for 15%)
    - Tax Amount
    - Total Amount (After Tax)
    - Mode of Payment
    - Pay Later Date (*Optional*)
    - An array of Sold Items Object. Object fields are:
        * Product
        * Unit
        * Quantity
        * Price
        * Amount
    - Status (Available values are `PENDING`, `COMPLETED`, and `FAILED`)
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Payment.objects.filter(status=Payment.COMPLETED)
    serializer_class = PaymentSerializer
    permission_classes = [IsBusinessOwnedPayment]

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by the current business account
        business_id = self.kwargs.get('business_id')
        qs = qs.filter(order__business_account__id=business_id)

        # Filter by mode of payment
        mode_of_payment_query = self.request.query_params.get('modeOfPayment')
        if mode_of_payment_query is not None:
            qs = qs.filter(mode_of_payment=mode_of_payment_query)

        # Filter by customer name
        customer_query = self.request.query_params.get('customer')
        if customer_query is not None:
            qs = qs.filter(order__customer__name__icontains=customer_query)
        return qs
