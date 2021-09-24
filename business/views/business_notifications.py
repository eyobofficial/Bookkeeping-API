from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, \
    UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from drf_yasg import openapi
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
        manual_parameters=[
            openapi.Parameter(
                'search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=_('Filter result by all or part of a notification type.')
            )
        ],
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

    retrieve:
    Notification Detail

    Returns a detail of a notification owned by the current business account.

    update:
    Notification Update

    Mark an existing notification object for the current business account
    as seeen.

    partial_update:
    Notification Update Partial

    Mark an existing notification object for the current business account
    as seeen.
    """
    queryset = Notification.objects.filter(is_seen=False)
    serializer_class = NotificationSerializer
    permission_classes = [IsBusinessOwnedResource]

    def get_queryset(self):
        qs = super().get_queryset()
        search_query = self.request.query_params.get('search')
        if search_query is not None:
            qs = qs.filter(notification_type__icontains=search_query)
        return qs
