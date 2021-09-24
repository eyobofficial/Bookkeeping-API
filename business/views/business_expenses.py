from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, \
    RetrieveModelMixin

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from expenses.models import Expense

from business.serializers import BusinessExpenseSerializer
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
        manual_parameters=[
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Search expenses by their title.')
            ),
        ],
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

    retrieve:
    Expense Detail

    Returns the details of an expense record.

    create:
    Expense Create

    Creates a new expense record for the current business account.
    """
    queryset = Expense.objects.all()
    serializer_class = BusinessExpenseSerializer
    permission_classes = [IsBusinessOwnedResource]

    def get_queryset(self):
        qs = super().get_queryset()
        search_query = self.request.query_params.get('search')
        if search_query is not None:
            qs = qs.filter(title__icontains=search_query)
        return qs
