from rest_framework.permissions import BasePermission

from users_app.models import Profile


class IsBusinessUser(BasePermission):
    """Allow access only to users with a business profile."""

    message = "Only business users can create offers."

    def has_permission(self, request, view):
        """Check whether the authenticated user is a business user."""
        profile = getattr(request.user, "profile", None)
        return bool(
            profile
            and profile.type == Profile.UserType.BUSINESS
        )
