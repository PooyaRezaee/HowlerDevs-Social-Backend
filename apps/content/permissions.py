from rest_framework import permissions


class IsContentOwner(permissions.BasePermission):
    message = "you not's content owner."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
