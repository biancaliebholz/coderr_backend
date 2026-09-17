"""Filters for review API endpoints."""

import django_filters

from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    """Filter reviews through the documented query parameters."""

    business_user_id = django_filters.NumberFilter(
        field_name="business_user_id",
    )
    reviewer_id = django_filters.NumberFilter(
        field_name="reviewer_id",
    )

    class Meta:
        """Define the model and supported filters."""

        model = Review
        fields = [
            "business_user_id",
            "reviewer_id",
        ]
