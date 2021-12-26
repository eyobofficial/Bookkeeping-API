from django.utils.translation import gettext_lazy as _

from rest_framework import permissions

from orders.models import Order
from payments.models import Payment


class IsAdminOrBusinessOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.user == user


class IsBusinessOwnedResource(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        business_accounts = user.business_accounts.all()
        return obj.business_account in business_accounts


class IsBusinessOwnedSoldItem(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        business_accounts = request.user.business_accounts.all()
        return obj.stock.business_account in business_accounts

    def has_permission(self, request, view):
        business_accounts = request.user.business_accounts.all()
        business_accounts_ids = [str(business_account.pk) for business_account in business_accounts]
        business_id = view.kwargs.get('business_id')
        return business_id in business_accounts_ids


class IsBusinessOwnedPayment(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        business_accounts = request.user.business_accounts.all()
        return obj.order.business_account in business_accounts


class IsOrderOpen(permissions.BasePermission):
    message = _('Updating or deleting closed order is not allowed.')

    def has_object_permission(self, request, view, obj):
        return obj.status == Order.OPEN


class IsPaymentNotCompleted(permissions.BasePermission):
    message = _('Updating completed payment is not allowed.')

    def has_object_permission(self, request, view, obj):
        return obj.status != Payment.COMPLETED
