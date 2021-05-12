from rest_framework import permissions


class IsAccountOwner(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        return obj == request.user
