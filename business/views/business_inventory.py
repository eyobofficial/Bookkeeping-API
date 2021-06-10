from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from inventory.models import Stock

from business.serializers import BusinessStockSerializer
from business.permissions import IsBusinessOwnedResource
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            200: BusinessStockSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            200: BusinessStockSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            201: BusinessStockSerializer(),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            200: BusinessStockSerializer(),
            401: shared_schema.unauthorized_401_response,
            400: 'Validation Error',
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            200: BusinessStockSerializer(),
            401: shared_schema.unauthorized_401_response,
            400: 'Validation Error',
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            204: 'No Content',
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
class BusinessStockViewSet(BaseBusinessAccountDetailViewSet, ModelViewSet):
    """
    list:
    Stock List

    Returns a list (array) of inventory stock objects for the
    current business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/inventory/stocks/`

    **Query Parameters** <br />
    - `search`: All or part of the product's name (case-insensitive) you are
    searching for.

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    retrieve:
    Stock Detail

    Returns the details of an inventory stock record.

    **HTTP Request** <br />
    `GET /business/{business_id}/inventory/stocks/{stock_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `stock_id`: The ID of the stock object.

    create:
    Stock Create

    Creates a new inventory stock record for the current business account.

    **HTTP Request** <br />
    `POST /business/{business_id}/inventory/stocks/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    update:
    Stock Update

    Updates the details of an inventory recored.

    **HTTP Request** <br />
    `PUT /business/{business_id}/inventory/stocks/{stock_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `stock_id`: The ID of the inventory stock object.

    partial_update:
    Stock Partial Update

    Partially updates the details of an inventory stock object.

    **HTTP Request** <br />
    `PATCH /business/{business_id}/inventory/stocks/{stock_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `stock_id`: The ID of the inventory stock object.

    destroy:
    Stock Delete

    Deletes an inventory stock recored.

    **HTTP Request** <br />
    `DELETE /business/{business_id}/inventory/stocks/{stock_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `stock_id`: The ID of the inventory stock object.
    """
    queryset = Stock.objects.all()
    serializer_class = BusinessStockSerializer
    permissions_classes = [IsBusinessOwnedResource]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            search_query = self.request.query_params.get('search')
            if search_query is not None:
                qs = qs.filter(product__icontains=search_query)
        return qs