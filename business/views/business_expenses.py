from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, \
    RetrieveModelMixin
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from expenses.models import Expense
from inventory.models import Stock

from business.serializers import BusinessExpenseSerializer, BusinessStockSerializer
from business.permissions import IsBusinessOwnedResource
from .base import BaseBusinessAccountDetailViewSet


# Mixins & base views to be inherited by the `BusinesssAccountExpenseViewset`
expense_mixins = (
    BaseBusinessAccountDetailViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
)


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Expenses'],
        responses={
            200: BusinessExpenseSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Expenses'],
        responses={
            200: BusinessExpenseSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        tags=['Expenses'],
        responses={
            201: BusinessExpenseSerializer(),
            400: 'Validation Error',  # TODO: Change to sample reponse
            401: shared_schema.unauthorized_401_response
        }
    )
)
class BusinessExpenseViewSet(*expense_mixins):
    """
    list:
    Expense List

    Returns a list (array) of expense objects for the current business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/expenses/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    retrieve:
    Expense Detail

    Returns the details of an expense record.

    **HTTP Request** <br />
    `GET /business/{business_id}/expenses/{id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `id`: The ID of the expense.

    create:
    Expense Create

    Creates a new expense record for the current business account.

    **HTTP Request** <br />
    `POST /business/{business_id}/expenses/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    """
    queryset = Expense.objects.all()
    serializer_class = BusinessExpenseSerializer
    permission_classes = [IsBusinessOwnedResource]
