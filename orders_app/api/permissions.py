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


class IsAssignedBusinessUser(BasePermission):
    """Allow updates only by the order's assigned provider."""

    def has_permission(self, request, view):
        """Check whether the user has a business profile."""
        profile = getattr(request.user, "profile", None)
        return bool(
            profile
            and profile.type == Profile.UserType.BUSINESS
        )

    def has_object_permission(self, request, view, obj):
        """Check whether the provider owns this order."""
        return obj.business_user_id == request.user.id
