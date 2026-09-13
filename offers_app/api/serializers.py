from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


User = get_user_model()


class OfferUserSerializer(serializers.ModelSerializer):
    """Serialize the documented public data of an offer creator."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
        ]


class OfferDetailReferenceSerializer(serializers.ModelSerializer):
    """Serialize an offer detail through its ID and API URL."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url",
        ]

    def get_url(self, obj):
        """Return the API URL of an offer detail."""
        path = f"/api/offerdetails/{obj.pk}/"
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(path)
        return path


class OfferListSerializer(serializers.ModelSerializer):
    """Serialize one offer in the public offer list."""

    user = serializers.IntegerField(
        source="user_id",
        read_only=True,
    )
    details = OfferDetailReferenceSerializer(
        many=True,
        read_only=True,
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )
    min_delivery_time = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )
    user_details = OfferUserSerializer(
        source="user",
        read_only=True,
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serialize one offer for the detail endpoint."""

    user = serializers.IntegerField(
        source="user_id",
        read_only=True,
    )
    details = OfferDetailReferenceSerializer(
        many=True,
        read_only=True,
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )
    min_delivery_time = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]


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
