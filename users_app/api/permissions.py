from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow profile reads and restrict changes to the profile owner."""

    def has_object_permission(self, request, view, obj):
        """Check whether the requested operation is permitted."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
