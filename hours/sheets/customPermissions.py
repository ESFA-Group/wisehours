from rest_framework import permissions

class IsFoodManager(permissions.BasePermission):
    """
    Allows access only to FoodManagers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_FoodManager)
