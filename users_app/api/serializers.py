from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import (
    validate_password as validate_django_password,
)
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users_app.models import Profile


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a complete user account."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=Profile.UserType.choices,
        write_only=True,
    )
    token = serializers.CharField(
        source="auth_token.key",
        read_only=True,
    )
    user_id = serializers.IntegerField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "token",
            "username",
            "email",
            "user_id",
            "password",
            "repeated_password",
            "type",
        ]

    def validate_email(self, value):
        """Reject an email address that is already registered."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email is already in use."
            )
        return value

    def validate(self, attrs):
        """Validate matching passwords and Django password rules."""
        if attrs["password"] != attrs["repeated_password"]:
            message = {
                "repeated_password": "Passwords do not match."
            }
            raise serializers.ValidationError(message)
        candidate = User(
            username=attrs["username"],
            email=attrs["email"],
        )
        validate_django_password(attrs["password"], user=candidate)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create the user, profile, and authentication token."""
        profile_type = validated_data.pop("type")
        validated_data.pop("repeated_password")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, type=profile_type)
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and return the authenticated user."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the submitted username and password."""
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )
        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize profile data together with related user data."""

    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
    )
    created_at = serializers.DateTimeField(
        source="user.date_joined",
        read_only=True,
    )
    type = serializers.CharField(read_only=True)
    file = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]

    def validate_email(self, value):
        """Reject an email address used by another user."""
        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.user_id
            )
        if queryset.exists():
            raise serializers.ValidationError(
                "Email is already in use."
            )
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update profile fields and writable user fields together."""
        user_data = validated_data.pop("user", {})
        self._update_user(instance.user, user_data)
        return super().update(instance, validated_data)

    def _update_user(self, user, user_data):
        """Save the changed fields belonging to the user model."""
        for field, value in user_data.items():
            setattr(user, field, value)
        if user_data:
            user.save(update_fields=list(user_data))
