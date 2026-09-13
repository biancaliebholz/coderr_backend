"""Filter definitions for offer API endpoints."""

import django_filters

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Filter offers through their creator and calculated detail values."""

    creator_id = django_filters.NumberFilter(
        field_name="user_id",
    )
    min_price = django_filters.NumberFilter(
        field_name="min_price",
        lookup_expr="gte",
    )
    max_delivery_time = django_filters.NumberFilter(
        field_name="min_delivery_time",
        lookup_expr="lte",
    )

    class Meta:
        model = Offer
        fields = []
