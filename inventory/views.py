from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared import schema as shared_schema
from inventory import schema as inventory_schema

from .models import Barcode
from .serializers import BarcodeSerializer, BarcodeFindSerializer


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_id='inventory-barcode-list',
        tags=['Barcodes'],
        responses={
            '200': BarcodeSerializer(many=True),
            '401': shared_schema.unauthorized_401_response,
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_id='inventory-barcode-detail',
        tags=['Barcodes'],
        responses={
            '200': BarcodeSerializer,
            '401': shared_schema.unauthorized_401_response,
            '404': shared_schema.not_found_404_response
        }
    )
)
class BarcodeViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
    Barcode List

    Returns the list of barcode objects in the database. The returned list include:
    - All *verified* barcodes, Or
    - *Non-verified* barcodes that are created by the current user

    retrieve:
    Barcode Detail

    Returns a detail of a single barcode objects in database using their ID. Only *verified*
    and *non-archived* barcodes are returned.
    """
    queryset = Barcode.objects.filter(archived=False, verified=True)
    serializer_class = BarcodeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='inventory-barcode-find',
        tags=['Barcodes'],
        responses={
            200: BarcodeSerializer,
            400: inventory_schema.barcode_number_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
    @action(detail=False, methods=['post'], serializer_class=BarcodeFindSerializer)
    def find(self, request, *args, **kwargs):
        """
        Barcode Find

        Find and return the details of a single matched barcode object using the
        barcode number. Only *verified* and *non-archived* barcodes are returned.
        """
        serializer = BarcodeFindSerializer(data=request.data)
        if serializer.is_valid():
            barcode_number = serializer.validated_data['barcode_number']
            barcode = get_object_or_404(Barcode, barcode_number=barcode_number)
            data = BarcodeSerializer(barcode).data
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
