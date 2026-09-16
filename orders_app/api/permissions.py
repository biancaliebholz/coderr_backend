"""Custom permissions for the orders API."""

from rest_framework.permissions import BasePermission

from users_app.models import Profile


class IsCustomer(BasePermission):
    """Allow access only to users with a customer profile."""

    def has_permission(self, request, view):
        """Check whether the authenticated user is a customer."""
        profile = getattr(request.user, "profile", None)
        return bool(
            profile
            and profile.type == Profile.UserType.CUSTOMER
        )
