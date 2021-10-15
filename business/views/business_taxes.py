from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ModelViewSet

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema

from business.models import BusinessAccountTax
from business.serializers import BusinessAccountTaxSerializer
from business.permissions import IsBusinessOwnedResource
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Business Account Tax'],
        manual_parameters=[
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Search Tax by their name.')
            ),
        ],
        responses={
            200: BusinessAccountTaxSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Business Account Tax'],
        responses={
            200: BusinessAccountTaxSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        tags=['Business Account Tax'],
        responses={
            201: BusinessAccountTaxSerializer(),
            400: 'Validation Error',  # TODO: Change to sample reponse
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        tags=['Business Account Tax'],
        responses={
            200: BusinessAccountTaxSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response,
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        tags=['Business Account Tax'],
        responses={
            200: BusinessAccountTaxSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        tags=['Business Account Tax'],
        responses={
            204: 'No Content',
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
class BusinessTaxViewSet(BaseBusinessAccountDetailViewSet, ModelViewSet):
    """
    list:
    Tax List

    Returns a list (array) of tax objects for the current business account.

    retrieve:
    Tax Detail

    Returns the details of a tax record.

    create:
    Tax Create

    Creates a new tax record for the current business account.

    update:
    Tax Update

    Updates the details of a tax recored for the current business account.

    partial_update:
    Tax Partial Update

    Partial updates the details of a tax recored for the current business account.

    destroy:
    Tax Delete

    Deletes a tax recored for the current business account.
    """
    queryset = BusinessAccountTax.objects.all()
    serializer_class = BusinessAccountTaxSerializer
    permission_classes = [IsBusinessOwnedResource]

    def get_queryset(self):
        qs = super().get_queryset()
        search_query = self.request.query_params.get('search')
        if search_query is not None:
            qs = qs.filter(name__icontains=search_query)
        return qs
