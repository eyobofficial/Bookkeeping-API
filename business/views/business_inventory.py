from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from inventory import schema as inventory_schema
from inventory.models import Stock, Sold
from inventory.serializers import BarcodeFindSerializer

from business import schema as business_schema
from business.serializers import BusinessStockSerializer, RestockingSerializer, \
    BusinessSoldSerializer
from business.permissions import IsBusinessOwnedResource, \
    IsBusinessOwnedSoldItem
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        manual_parameters=[
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by all or part of a product name.')
            )
        ],
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
        request_body=business_schema.stock_request_body,
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
        request_body=business_schema.stock_request_body,
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
        request_body=business_schema.stock_request_body,
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

    retrieve:
    Stock Detail

    Returns the details of an inventory stock record.

    create:
    Stock Create

    Creates a new inventory stock record for the current business account.

    update:
    Stock Update

    Updates the details of an inventory recored.

    partial_update:
    Stock Partial Update

    Partially updates the details of an inventory stock object.

    destroy:
    Stock Delete

    Deletes an inventory stock recored.
    """
    queryset = Stock.objects.all()
    serializer_class = BusinessStockSerializer
    permission_classes = [IsBusinessOwnedResource]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            search_query = self.request.query_params.get('search')
            if search_query is not None:
                qs = qs.filter(product__icontains=search_query)
        return qs

    @swagger_auto_schema(
        operation_id='inventory-stock-barcode-find',
        tags=['Inventory'],
        responses={
            200: BusinessStockSerializer,
            400: inventory_schema.barcode_number_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
    @action(detail=False, methods=['post'], serializer_class=BarcodeFindSerializer)
    def barcode(self, request, *args, **kwargs):
        """
        Stock Barcode Find

        Find and return the details of a single matched inventory stock object using the
        barcode number.
        """
        serializer = BarcodeFindSerializer(data=request.data)
        if serializer.is_valid():
            barcode_number = serializer.validated_data['barcode_number']
            queryset = self.get_queryset()
            stock = get_object_or_404(queryset, barcode_number=barcode_number)
            data = BusinessStockSerializer(stock).data
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_id='inventory-stock-restocking',
        tags=['Inventory'],
        request_body=RestockingSerializer(),
        responses={
            200: RestockingSerializer,
            400: inventory_schema.barcode_number_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
    @action(detail=True, methods=['put'], serializer_class=RestockingSerializer)
    def restock(self, request, *args, **kwargs):
        """
        Restock Inventory

        Restock an inventory item by adding additional quantity to the instance. This
        also updates the `lastRestockedDate` field with the current datetime timestamp.
        """
        stock = self.get_object()
        serializer = RestockingSerializer(stock, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        manual_parameters=[
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by all or part of a product name.')
            )
        ],
        responses={
            200: BusinessSoldSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Inventory'],
        responses={
            200: BusinessSoldSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
class SoldInventoryViewSet(ReadOnlyModelViewSet):
    """
    list:
    Sold Inventory List

    Returns a list (array) of sold inventory objects for the
    current business account.

    retrieve:
    Sold Inventory Detail

    Returns the details of a sold inventory record.
    """
    queryset = Sold.objects.filter(quantity__gt=0)
    serializer_class = BusinessSoldSerializer
    permission_classes = [IsBusinessOwnedSoldItem]

    def get_queryset(self):
        qs = super().get_queryset()
        business_id = self.kwargs.get('business_id')
        qs = qs.filter(stock__business_account__id=business_id)
        if self.action == 'list':
            search_query = self.request.query_params.get('search')
            if search_query is not None:
                qs = qs.filter(stock__product__icontains=search_query)
        return qs
