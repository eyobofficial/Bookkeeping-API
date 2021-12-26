from rest_framework import permissions


class IsAccountActive(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.is_active


class IsAccountOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsProfileOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj == request.user.profile


class IsBusinessOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsSettingOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj == request.user.settings
