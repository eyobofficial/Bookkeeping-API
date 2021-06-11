from rest_framework import permissions


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
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        business_accounts = user.business_accounts.all()
        return obj.business_account in business_accounts


class IsBusinessOwnedSoldItem(permissions.IsAuthenticated):
    """
    Check if a `Sold` instance is owned by a business owner.
    """

    def has_object_permission(self, request, view, obj):
        business_accounts = request.user.business_accounts.all()
        return obj.stock.business_account in business_accounts
