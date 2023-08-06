from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_admin
