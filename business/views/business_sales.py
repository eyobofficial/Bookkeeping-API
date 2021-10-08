from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from payments.models import Payment
from business.serializers import PaymentSerializer
from business.permissions import IsBusinessOwnedPayment
from payments.filters import SalesFilter


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_id='business-sales-list',
        tags=['Sales'],
        manual_parameters=[
            openapi.Parameter(
                'customer',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_(('Filter result by all or part of the '
                               'customer name, phone number, or email.')),
            ),
            openapi.Parameter(
                'modeOfPayment',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by the mode of payment used.'),
                enum=('cash', 'bank', 'card', 'credit')
            ),
            openapi.Parameter(
                'date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_(
                    'Filter result by the date of the sales. Date format: `yyyy-mm-dd`.'
                )
            ),
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_(('Filter result by customer name, customer phone number, '
                               'customer email, sales description, or sales created date. '
                               'For searching by date, use the format `yyyy-mm-dd`.')),
            ),
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

    retrieve:
    Sales Detail

    Returns a detail of completed sales instance for the current business
    account. Completed sales are the same as payments objects with a status
    of `COMPLETED`.
    """
    queryset = Payment.objects.filter(status=Payment.COMPLETED)
    serializer_class = PaymentSerializer
    permission_classes = [IsBusinessOwnedPayment]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SalesFilter

    def get_queryset(self):
        qs = super().get_queryset()
        business_id = self.kwargs.get('business_id')
        return qs.filter(order__business_account__id=business_id)

    def get_business_account(self):
        """
        Return the current active business account.
        """
        business_id = self.kwargs.get('business_id')
        user_business_accounts = self.request.user.business_accounts.all()
        return get_object_or_404(user_business_accounts, pk=business_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['business_account'] = self.get_business_account()
        context['request'] = self.request
        return context
