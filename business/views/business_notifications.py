from django.utils.decorators import method_decorator

from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, \
    UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from drf_yasg.utils import swagger_auto_schema

from notifications.models import Notification

from business.serializers import NotificationSerializer
from business.permissions import IsBusinessOwnedResource
from .base import BaseBusinessAccountDetailViewSet


cls_mixins = (
    BaseBusinessAccountDetailViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet
)


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_id='business-notification-list',
        tags=['Notifications'],
        responses={
            200: NotificationSerializer(many=True),
            401: 'Unauthorized'
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_id='payment-notification-detail',
        tags=['Notifications'],
        responses={
            200: NotificationSerializer(),
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        operation_id='business-notification-update',
        tags=['Notifications'],
        responses={
            200: NotificationSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_id='business-notification-update-partial',
        tags=['Notifications'],
        responses={
            200: NotificationSerializer(),
            400: 'Validation Error',
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
)
class NotificationViewSet(*cls_mixins):
    """
    list:
    Notification List

    Returns a list (array) of all notifications for the current business
    account.

    **HTTP Request** <br />
    `GET /business/{business_id}/notifications/`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.

    **Response Body** <br />
    An array of a notification object which includes:
    - Notification ID
    - Notification Type
    - Action Message
    - Action Date and Time
    - Action Date Label
    - Action URL
    - Seen
    - Create Date & Time
    - Last Updated Date & Time

    retrieve:
    Notification Detail

    Returns a detail of a notification owned by the current business account.

    **HTTP Request** <br />
    `GET /business/{business_id}/notifications/{notification_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `notification_id`: The ID of the notification object.

    **Response Body** <br />
    - Notification ID
    - Notification Type
    - Action Message
    - Action Date and Time
    - Action Date Label
    - Action URL
    - Seen
    - Create Date & Time
    - Last Updated Date & Time

    update:
    Notification Update

    Mark an existing notification object for the current business account
    as seeen.

    **HTTP Request** <br />
    `GET /business/{business_id}/notifications/{notification_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `notification_id`: The ID of the notification object.

    **Request Body Parameters**
    - isSeen (*boolean**)

    **Response Body** <br />
    - Notification ID
    - Notification Type
    - Action Message
    - Action Date and Time
    - Action Date Label
    - Action URL
    - Seen
    - Create Date & Time
    - Last Updated Date & Time

    partial_update:
    Notification Update Partial

    Mark an existing notification object for the current business account
    as seeen.

    **HTTP Request** <br />
    `GET /business/{business_id}/notifications/{notification_id}`

    **URL Parameters** <br />
    - `business_id`: The ID of the business account.
    - `notification_id`: The ID of the notification object.

    **Request Body Parameters**
    - isSeen (*boolean**)

    **Response Body** <br />
    - Notification ID
    - Notification Type
    - Action Message
    - Action Date and Time
    - Action Date Label
    - Action URL
    - Seen
    - Create Date & Time
    - Last Updated Date & Time
    """
    queryset = Notification.objects.filter(is_seen=False)
    serializer_class = NotificationSerializer
    permission_classes = [IsBusinessOwnedResource]
