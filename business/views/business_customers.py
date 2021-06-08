from PIL import Image

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, UnsupportedMediaType
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from business import schema as business_schema
from shared.parsers import PhotoUploadParser
from shared.utils.filetypes import get_mime_type, build_filename_ext
from customers.models import Customer

from business.serializers import BusinessCustomerSerializer
from business.permissions import IsBusinessOwnedResource
from .base import BaseBusinessAccountDetailViewSet


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Customers'],
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
        responses={
            201: BusinessCustomerSerializer(),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='update',
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
    name='partial_update',
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

    @swagger_auto_schema(
        operation_id='customer-photo-upload',
        responses={
            200: business_schema.customer_photo_upload_200_response,
            400: business_schema.customer_photo_upload_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response,
            415: business_schema.customer_photo_upload_415_response
        },
        tags=['Customers']
    )
    @action(
        detail=True, methods=['put'],
        parser_classes=[PhotoUploadParser],
        serializer_class=None
    )
    def photo(self, request, business_id=None, pk=None, format=None):
        """
        Customers Photo Upload

        Upload a new photo for a customer of a business account. Files are uploaded
        as a form data. Only image files are accepted by the endpoint.

        **HTTP Request** <br />
        `PUT /business/{business_id}/customers/{customer_id}/photo/`

        **URL Parameters** <br />
        - `business_id`: The ID of the business account.
        - `customer_id`: The ID of the customer.
        """
        customer = self.get_object()
        file_obj = request.data.get('file')

        if file_obj is None:
            raise ParseError(_('No image file included.'))

        # Media/Mime Type
        media_type = get_mime_type(file_obj)

        try:
            img = Image.open(file_obj)
            img.verify()
        except:
            err_message = _(f'Unsupported file type.')
            raise UnsupportedMediaType(media_type, detail=err_message)
        filename = build_filename_ext(customer.name, media_type)
        customer.photo.save(filename, file_obj, save=True)
        message = {'detail': _('Customer photo is uploaded.')}
        return Response(message, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='customer-photo-remove',
        responses={
            204: business_schema.customer_photo_remove_204_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        },
        tags=['Customers']
    )
    @photo.mapping.delete
    def delete_photo(self, request, business_id=None, pk=None, format=None):
        """
        Customers Photo Remove

        Remove the customer photo of a business account.

        **HTTP Request** <br />
        `DELETE /business/{business_id}/customers/{customer_id}/photo/`

        **URL Parameters** <br />
        - `business_id`: The ID of the business account.
        - `customer_id`: The ID of the customer.
        """
        customer = self.get_object()
        customer.photo.delete(save=True)
        message = {'detail': _('Customer photo is deleted.')}
        return Response(message, status=status.HTTP_204_NO_CONTENT)
