from PIL import Image

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from business import schema as business_schema
from customers.models import Customer
from business.serializers import BusinessCustomerSerializer
from business.permissions import IsBusinessOwnedResource
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Customers'],
        manual_parameters=[
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by all or part of a customer name.')
            )
        ],
        responses={
            200: BusinessCustomerSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Customers'],
        responses={
            200: BusinessCustomerSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        tags=['Customers'],
        request_body=business_schema.customer_edit_request_body,
        responses={
            201: BusinessCustomerSerializer(),
            401: shared_schema.unauthorized_401_response,
            409: business_schema.duplicate_409_response
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        tags=['Customers'],
        request_body=business_schema.customer_edit_request_body,
        responses={
            200: BusinessCustomerSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response,
            409: business_schema.duplicate_409_response
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        tags=['Customers'],
        request_body=business_schema.customer_edit_request_body,
        responses={
            200: BusinessCustomerSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        tags=['Customers'],
        responses={
            204: 'No Content',
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
class BusinessCustomerViewSet(BaseBusinessAccountDetailViewSet, ModelViewSet):
    """
    list:
    Customers List

    Returns a list of customers for the current business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/customers/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Query Parameters** <br />
    - `search`: All or part of the customer's name (case-insensitive) you are
    searching for.

    retrieve:
    Customers Detail

    Returns the details of a customer recored.

    **HTTP Request** <br />
    `GET /business/{business_id}/customers/{customer_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `customer_id`: The ID of the customer.

    create:
    Customers Create

    Creates a new customer recored for the current business account.

    **HTTP Request** <br />
    `POST /business/{business_id}/customers/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    update:
    Cutomers Update

    Updates the details of a customer recored.

    **HTTP Request** <br />
    `PUT /business/{business_id}/customers/{customer_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `customer_id`: The ID of the customer.

    partial_update:
    Cutomers Partial Update

    Partially updates the details of a customer recored.

    **HTTP Request** <br />
    `PATCH /business/{business_id}/customers/{customer_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `customer_id`: The ID of the customer.

    destroy:
    Customers Delete

    Deletes a customer recored.

    **HTTP Request** <br />
    `DELETE /business/{business_id}/customers/{customer_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `customer_id`: The ID of the customer.
    """
    queryset = Customer.objects.all()
    serializer_class = BusinessCustomerSerializer
    permission_classes = [IsBusinessOwnedResource]

    def get_queryset(self):
        qs = super().get_queryset()
        search_query = self.request.query_params.get('search')
        if search_query is not None:
            qs = qs.filter(name__icontains=search_query)
        return qs

