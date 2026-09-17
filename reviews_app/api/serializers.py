from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review
from users_app.models import Profile


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize reviews for listing and later updating."""

    class Meta:
        """Define the model and exposed fields."""

        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "business_user",
            "reviewer",
            "created_at",
            "updated_at",
        ]


class ReviewCreateSerializer(ReviewSerializer):
    """Validate and create a customer review."""

    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta(ReviewSerializer.Meta):
        """Make the reviewed business writable during creation."""

        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
            "updated_at",
        ]
        validators = []

    def validate_business_user(self, value):
        """Require the reviewed user to have a business profile."""
        profile = getattr(value, "profile", None)
        if not profile:
            raise serializers.ValidationError(
                "The selected user has no profile."
            )
        if profile.type != Profile.UserType.BUSINESS:
            raise serializers.ValidationError(
                "Only business users can be reviewed."
            )
        return value

    def validate(self, attrs):
        """Reject a second review for the same business user."""
        reviewer = self.context["request"].user
        business_user = attrs["business_user"]
        duplicate_exists = Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists()
        if duplicate_exists:
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return attrs
