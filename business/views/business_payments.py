from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, \
    UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from payments.models import Payment
from business.serializers import PaymentSerializer
from business.permissions import IsBusinessOwnedPayment, IsPaymentNotCompleted
from notifications.helpers.payment_notifications import pay_later_reminder


# Arguments for `BusinessPaymentViewSet`
cls_args = (
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
)


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_id='business-payment-list',
        tags=['Payments'],
        manual_parameters=[
            openapi.Parameter(
                'modeOfPayment',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by the mode of payment.'),
                enum=('CASH', 'BANK', 'CARD', 'CREDIT')
            ),
            openapi.Parameter(
                'status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by the status of payment.'),
                enum=('PENDING', 'COMPLETED', 'FAILED')
            ),
            openapi.Parameter(
                'orderId',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by ID of an order object.')
            ),
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by customer name or phone number.')
            )
        ],
        responses={
            200: PaymentSerializer(many=True),
            401: 'Unauthorized'
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_id='business-payment-create',
        tags=['Payments'],
        responses={
            201: PaymentSerializer(),
            401: 'Unauthorized',
            400: 'Validation Errors'
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'order': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_UUID
                ),
                'modeOfPayment': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['CASH', 'CARD', 'CREDIT', 'BANK']
                ),
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['PENDING', 'COMPLETED', 'FAILED'],
                    default='PENDING'
                ),
                'payLaterDate': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE
                )
            }
        )
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_id='business-payment-detail',
        tags=['Payments'],
        responses={
            200: PaymentSerializer(),
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        operation_id='business-payment-update',
        tags=['Payments'],
        responses={
            200: PaymentSerializer(),
            400: 'Validation Errors',
            401: 'Unauthorized',
            403: 'Updating completed payment is not allowed.',
            404: 'Not Found'
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_id='business-payment-partial-update',
        tags=['Payments'],
        responses={
            200: PaymentSerializer(),
            400: 'Validation Errors',
            401: 'Unauthorized',
            403: 'Updating completed payment is not allowed.',
            404: 'Not Found'
        }
    )
)
class BusinessPaymentViewSet(*cls_args):
    """
    list:
    Payment List

    Returns a list (array) of all payments for the current business account.

    retrieve:
    Payment Detail

    Returns a detail of a payment owned by the current business account.

    create:
    Payment Create

    Creates a new payment object for the current business account.

    **Validation Error Events** <br />
    - `orderId` and `modeOfPayments` are all required.
    - `payLaterDate` field is required if `modeOfPayment` has a value `CREDIT`.
    - `orderId` must be unique.
    - `payLaterDate` cannot be date in the past.

    update:
    Payment Update

    Updates an existing payment object for the current business account.

    **Validation Error Events** <br />
    - `orderId` and `modeOfPayments` are all required.
    - `payLaterDate` field is required if `modeOfPayment` has a value `CREDIT`.
    - `orderId` must be unique.
    - `payLaterDate` cannot be date in the past.

    partial_update:
    Payment Partial Update

    Partially updates attributes of an existing payment object for the
    current business account.

    **Validation Error Events** <br />
    - `orderId` and `modeOfPayments` are all required.
    - `payLaterDate` field is required if `modeOfPayment` has a value `CREDIT`.
    - `orderId` must be unique.
    - `payLaterDate` cannot be date in the past.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsBusinessOwnedPayment]

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by the current business account
        business_id = self.kwargs.get('business_id')
        qs = qs.filter(order__business_account__id=business_id)

        # Filter by the order_id
        order_id_query = self.request.query_params.get('orderId')
        if order_id_query is not None:
            qs = qs.filter(order__pk=order_id_query)

        # Filter by mode of payment
        mode_of_payment_query = self.request.query_params.get('modeOfPayment')
        if mode_of_payment_query is not None:
            qs = qs.filter(mode_of_payment=mode_of_payment_query)

        # Filter by payment status
        status_query = self.request.query_params.get('status')
        if status_query is not None:
            qs = qs.filter(status=status_query)

        # Search by customer name or phone number
        search_query = self.request.query_params.get('search')
        if search_query is not None:
            qs = qs.filter(
                Q(order__customer__name__icontains=search_query) |
                Q(order__customer__phone_number__icontains=search_query)
            )
        return qs

    @swagger_auto_schema(
        operation_id='business-payment-receipt',
        tags=['Payments'],
        responses={
            200: 'A PDF Download URL',
            401: 'Unauthorized',
            404: 'Not Found',
        }
    )
    @action(detail=True, serializer_class=None)
    def receipt(self, request, business_id=None, pk=None):
        """
        Payment Receipt

        Returns a URL to PDF receipt file for the current payment object.
        """
        payment = self.get_object()
        payment.generate_pdf(request)
        response = HttpResponse(payment.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Receipt.pdf"'
        return response

    def perform_create(self, serializer):
        payment = serializer.save()

        # Create reminder for completed `PAY LATER` payments
        if (payment.mode_of_payment == Payment.CREDIT
            and payment.status == Payment.COMPLETED):
            business_id = self.kwargs.get('business_id')
            pay_later_reminder(payment, business_id, self.request)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes += [IsPaymentNotCompleted]
        return [permission() for permission in self.permission_classes]
