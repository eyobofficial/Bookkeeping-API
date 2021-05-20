from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema
from customers.models import Customer

from .models import BusinessType, BusinessAccount
from .serializers import BusinessTypeSerializer, BusinessAccountSerializer, \
    BusinessCustomerSerializer
from .permissions import IsAdminOrBusinessOwner, IsCustomerOwner


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Bussiness Account'],
        responses={
            200: BusinessTypeSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Bussiness Account'],
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
    `GET /business/types/{id}/`

    **URL Parameters** <br />
    - `id`: The ID of the business type.

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
        tags=['Bussiness Account'],
        responses={
            200: BusinessAccountSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Bussiness Account'],
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
    - Business Type
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
    `GET /business/{id}`

    **URL Parameters** <br />
    - `id`: The ID of the business account.

    **Response Body** <br />
    - Business ID
    - User ID
    - Business Type ID
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
class BusinessCustomerViewSet(ModelViewSet):
    """
    list:
    Customers List

    Returns a list of customers for the current business account.

    retrieve:
    Customers Detail

    Returns the details of a customer recored.

    create:
    Customers Create

    Creates a new customer recored for the current business account.

    update:
    Cutomers Update

    Updates the details of a customer recored.

    partial_update:
    Cutomers Partial Update

    Partially updates the details of a customer recored.

    destroy:
    Customers Delete

    Deletes a customer recored.
    """
    queryset = Customer.objects.all()
    serializer_class = BusinessCustomerSerializer
    permission_classes = [IsCustomerOwner]

    def get_queryset(self):
        qs = super().get_queryset()
        business_id = self.kwargs.get('business_id')
        return qs.filter(business_account__id=business_id)

    def perform_create(self, serializer):
        business_id = self.kwargs.get('business_id')
        business_account = get_object_or_404(BusinessAccount, pk=business_id)
        serializer.save(business_account=business_account)
