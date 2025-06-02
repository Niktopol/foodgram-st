from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrAuthor(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.author == request.user
