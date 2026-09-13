from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialize one package belonging to an offer."""

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]


class OfferCreateSerializer(serializers.ModelSerializer):
    """Create an offer together with exactly three details."""

    details = OfferDetailSerializer(many=True)
    image = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]

    def validate_details(self, value):
        """Require one basic, standard, and premium detail."""
        required_types = set(OfferDetail.OfferType.values)
        provided_types = {detail["offer_type"] for detail in value}

        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must contain exactly three details."
            )
        if provided_types != required_types:
            raise serializers.ValidationError(
                "Basic, standard and premium details are required."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create the offer and all nested details atomically."""
        details_data = validated_data.pop("details")
        if validated_data.get("image") is None:
            validated_data.pop("image", None)

        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer
