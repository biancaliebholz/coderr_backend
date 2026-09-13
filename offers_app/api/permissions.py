from rest_framework.permissions import BasePermission

from users_app.models import Profile


class IsBusinessUser(BasePermission):
    """Allow access only to users with a business profile."""

    message = "Only business users can create offers."

    def has_permission(self, request, view):
        """Check whether the user has a business profile."""
        profile = getattr(request.user, "profile", None)
        return bool(
            profile
            and profile.type == Profile.UserType.BUSINESS
        )


class IsOfferOwner(BasePermission):
    """Allow changes only by the creator of an offer."""

    message = "Only the offer owner may change this offer."

    def has_object_permission(self, request, view, obj):
        """Check whether the authenticated user owns the offer."""
        return obj.user_id == request.user.id
