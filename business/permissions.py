from rest_framework import permissions


class IsAdminOrBusinessOwner(permissions.IsAuthenticated):
    """
    Check if authenticated user is either an admin user
    (i.e. is_staff = True) or an owner of the business object.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.user == user
