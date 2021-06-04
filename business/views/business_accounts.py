from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema

from business.models import BusinessType, BusinessAccount
from business.serializers import BusinessTypeSerializer, BusinessAccountSerializer
from business.permissions import IsAdminOrBusinessOwner


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
