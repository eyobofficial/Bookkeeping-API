from rest_framework import permissions


class IsAccountActive(permissions.IsAuthenticated):
    """
    Check if an account is active (i.e. not disabled)
    """

    def has_object_permission(self, request, view, obj):
        return obj.is_active


class IsAccountOwner(permissions.IsAuthenticated):
    """
    Check if an account is owned by the current authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsProfileOwner(permissions.IsAuthenticated):
    """
    Check if a user profile is owned by the current authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user.profile


class IsSettingOwner(permissions.IsAuthenticated):
    """
    Check if a user settings is owned by the current authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user.settings
