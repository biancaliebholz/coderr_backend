from rest_framework.permissions import BasePermission

from users_app.models import Profile


class IsCustomerForReviewCreation(BasePermission):
    """Allow only customers to create reviews."""

    def has_permission(self, request, view):
        """Check the profile type for POST requests."""
        if request.method != "POST":
            return True
        profile = getattr(request.user, "profile", None)
        return bool(
            profile
            and profile.type == Profile.UserType.CUSTOMER
        )


class IsReviewOwner(BasePermission):
    """Allow changes only by the review's creator."""

    def has_object_permission(self, request, view, obj):
        """Compare the reviewer with the authenticated user."""
        return obj.reviewer_id == request.user.id
