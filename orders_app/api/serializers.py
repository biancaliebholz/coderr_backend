from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serialize the complete public representation of an order."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(OrderSerializer):
    """Create an order snapshot from an offer detail."""

    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta(OrderSerializer.Meta):
        fields = [
            "offer_detail_id",
            *OrderSerializer.Meta.fields,
        ]

    def validate_offer_detail_id(self, value):
        """Return the selected package or raise a 404 response."""
        queryset = OfferDetail.objects.select_related("offer__user")
        return get_object_or_404(queryset, pk=value)

    def create(self, validated_data):
        """Create an order from the selected package snapshot."""
        detail = validated_data.pop("offer_detail_id")
        snapshot = self._snapshot_data(detail)
        return Order.objects.create(
            customer_user=self.context["request"].user,
            business_user=detail.offer.user,
            **snapshot,
        )

    def _snapshot_data(self, detail):
        """Extract immutable package data from an offer detail."""
        return {
            "title": detail.title,
            "revisions": detail.revisions,
            "delivery_time_in_days": detail.delivery_time_in_days,
            "price": detail.price,
            "features": detail.features,
            "offer_type": detail.offer_type,
        }


class OrderStatusSerializer(OrderSerializer):
    """Allow updates to an order's status only."""

    status = serializers.ChoiceField(
        choices=Order.Status.choices,
    )

    class Meta(OrderSerializer.Meta):
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
            "updated_at",
        ]
