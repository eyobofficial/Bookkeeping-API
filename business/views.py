from django.utils.decorators import method_decorator

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema

from .models import BusinessType
from .serializers import BusinessTypeSerializer


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

    Returns a list of all business types.

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
