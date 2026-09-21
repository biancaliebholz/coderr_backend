from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


User = get_user_model()


def _remove_null_image(validated_data):
    """Ignore a null image value instead of saving it."""
    if validated_data.get("image") is None:
        validated_data.pop("image", None)


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
    """Serialize an offer detail as an ID and URL reference."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url",
        ]

    def get_url(self, obj):
        """Return the absolute or relative detail endpoint URL."""
        path = f"/api/offerdetails/{obj.pk}/"
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(path)
        return path


class OfferListSerializer(serializers.ModelSerializer):
    """Serialize offers for the paginated public list."""

    details = OfferDetailReferenceSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    min_delivery_time = serializers.IntegerField(read_only=True)
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
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialize all fields of one offer package."""

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


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serialize one offer with its detail references."""

    details = OfferDetailReferenceSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

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
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]


class OfferDetailUpdateSerializer(OfferDetailSerializer):
    """Validate fields used to update an existing offer detail."""

    id = serializers.IntegerField(required=False)
    offer_type = serializers.ChoiceField(
        choices=OfferDetail.OfferType.choices,
    )

    class Meta(OfferDetailSerializer.Meta):
        extra_kwargs = {
            "title": {"required": False},
            "revisions": {"required": False},
            "delivery_time_in_days": {"required": False},
            "price": {"required": False},
            "features": {"required": False},
        }


class OfferCreateSerializer(serializers.ModelSerializer):
    """Create an offer together with exactly three package details."""

    image = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    details = OfferDetailSerializer(many=True)

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
        """Require exactly one package of every supported type."""
        offer_types = {detail["offer_type"] for detail in value}
        required_types = set(OfferDetail.OfferType.values)
        if len(value) != 3 or offer_types != required_types:
            raise serializers.ValidationError(
                "Exactly one basic, standard and premium detail is required."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create an offer together with its package details."""
        details_data = validated_data.pop("details")
        _remove_null_image(validated_data)
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def _create_details(self, offer, details_data):
        """Create all package details belonging to an offer."""
        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data,
            )


class OfferUpdateSerializer(serializers.ModelSerializer):
    """Update an offer and selected nested package details."""

    image = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    details = OfferDetailUpdateSerializer(
        many=True,
        required=False,
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
        """Require a package type for each nested detail update."""
        if any("offer_type" not in detail for detail in value):
            raise serializers.ValidationError(
                "Each detail requires an offer_type."
            )
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update the offer and any supplied package details."""
        details_data = validated_data.pop("details", [])
        _remove_null_image(validated_data)
        instance = super().update(instance, validated_data)
        for detail_data in details_data:
            self._update_detail(instance, detail_data)
        return instance

    def _get_detail(self, offer, detail_data):
        """Find a detail by its type and optional ID."""
        detail_id = detail_data.pop("id", None)
        lookup = {"offer_type": detail_data["offer_type"]}
        if detail_id is not None:
            lookup["pk"] = detail_id
        try:
            return offer.details.get(**lookup)
        except OfferDetail.DoesNotExist as error:
            message = {"details": "Detail does not belong to this offer."}
            raise serializers.ValidationError(message) from error

    def _update_detail(self, offer, detail_data):
        """Update the supplied fields of one offer detail."""
        detail = self._get_detail(offer, detail_data)
        for field, value in detail_data.items():
            setattr(detail, field, value)
        detail.save()
