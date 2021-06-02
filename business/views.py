from PIL import Image

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, \
    GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, \
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from business import schema as business_schema
from shared.parsers import PhotoUploadParser
from shared.utils.filetypes import get_mime_type, build_filename_ext
from customers.models import Customer
from expenses.models import Expense
from inventory.models import Stock

from .models import BusinessType, BusinessAccount
from .serializers import BusinessTypeSerializer, BusinessAccountSerializer, \
    BusinessCustomerSerializer, BusinessExpenseSerializer, \
    BusinessStockSerializer
from .permissions import IsAdminOrBusinessOwner, IsCustomerOwner, IsExpenseOwner,\
    IsStockOwner


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: BusinessTypeSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: BusinessTypeSerializer(),
            401: shared_schema.unauthorized_401_response
        }
    )
)
class BusinessTypeViewSet(ReadOnlyModelViewSet):
    """
    list:
    Business Type List

    Returns a list of all business types. Examples: *Online Store*, *Fashion,
    Health, & Beauty*, *Cafe & Restaurants*, *Food & Drink*, *etc*.

    **HTTP Request** <br />
    `GET /business/types/`

    **Response Body** <br />
    The response body includes a list (array) of a business type objects. The
    business type object includes:
    - Business Type ID
    - Title

    retrieve:
    Business Type Detail

    Returns the details of a business type.

    **HTTP Request** <br />
    `GET /business/types/{business_id}/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business type.

    **Response Body** <br />
    - Business Type ID
    - Title
    """
    queryset = BusinessType.objects.all()
    serializer_class = BusinessTypeSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: BusinessAccountSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: BusinessAccountSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
class BusinessAccountViewSet(ReadOnlyModelViewSet):
    """
    list:
    Business Account List

    Returns a list of all business account. If the request is sent by:
      - A non-authenticted user, return a `401 Unauthorized` error response.
      - An authenticated admin user, return all the business accounts
      in the systems.
      - An authenticted non-admin user, return only the business accounts
      of the current authenticated user.

    **HTTP Request** <br />
    `GET /business/`

    **Response Body** <br />
    The response body includes a list (array) of a business account objects. The
    business account object includes:
    - Business ID
    - User ID
    - Business Type Object
    - Business Name
    - Currency
    - Country (*using [ISO 3166-1](https://en.wikipedia.org/wiki/ISO_3166-1) format*, *required*)
    - City
    - Address
    - Postal Code
    - Email Address
    - Created Date and Time
    - Last Updated Date and Time

    retrieve:
    Business Account Detail

    Returns the details of a business account.

    **HTTP Request** <br />
    `GET /business/{business_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Response Body** <br />
    - Business ID
    - User ID
    - Business Type Object
    - Business Name
    - Currency
    - Country (*using [ISO 3166-1](https://en.wikipedia.org/wiki/ISO_3166-1) format*)
    - City
    - Address
    - Postal Code
    - Email Address
    - Created Date and Time
    - Last Updated Date and Time
    """
    queryset = BusinessAccount.objects.all()
    serializer_class = BusinessAccountSerializer
    permission_classes = [IsAdminOrBusinessOwner]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs


class BaseBusinessAccountDetailViewSet:
    """
    Base view class for business account detail viewsets.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        business_id = self.kwargs.get('business_id')
        return qs.filter(business_account__id=business_id)

    def perform_create(self, serializer):
        business_id = self.kwargs.get('business_id')
        business_account = get_object_or_404(BusinessAccount, pk=business_id)
        serializer.save(business_account=business_account)



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
    permission_classes = [IsCustomerOwner]

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
    permission_classes = [IsExpenseOwner]


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
    permissions_classes = [IsStockOwner]
