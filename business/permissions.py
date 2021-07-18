from django.utils.translation import gettext_lazy as _

from rest_framework import permissions

from orders.models import Order
from payments.models import Payment


class IsAdminOrBusinessOwner(permissions.IsAuthenticated):
    """
    Check if authenticated user is either an admin user
    (i.e. is_staff = True) or an owner of the business object.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.user == user


class IsBusinessOwnedResource(permissions.IsAuthenticated):
    """
    Check if the current resource is owned by the active business
    account record.

    This resources include:
    - Customer
    - Expense
    - Inventory Stock
    - Customer Order
    - Notifications
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        business_accounts = user.business_accounts.all()
        return obj.business_account in business_accounts


class IsBusinessOwnedSoldItem(permissions.IsAuthenticated):
    """
    Check if a `Sold` instance belongs to a business account.
    """

    def has_object_permission(self, request, view, obj):
        business_accounts = request.user.business_accounts.all()
        return obj.stock.business_account in business_accounts


class IsBusinessOwnedPayment(permissions.IsAuthenticated):
    """
    Check if a `Payment` instance belongs to a business account.
    """

    def has_object_permission(self, request, view, obj):
        business_accounts = request.user.business_accounts.all()
        return obj.order.business_account in business_accounts


class IsOrderOpen(permissions.BasePermission):
    """
    Check if an `Order` instance has a status of `OPEN` before
    allowing updating and deleting the instance.
    """
    message = _('Updating or Deleting closed order is not allowed.')

    def has_object_permission(self, request, view, obj):
        return obj.status == Order.OPEN


class IsPaymentNotCompleted(permissions.BasePermission):
    """
    Check if a payment instane isn't completed yet before allowing
    updating and deleting.
    """
    message = _('Updating completed payment is not allowed.')

    def has_object_permission(self, request, view, obj):
        return obj.status != Payment.COMPLETED
