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
    user_id = serializers.IntegerField(source="id", read_only=True)

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
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            message = {"repeated_password": "Passwords do not match."}
            raise serializers.ValidationError(message)
        candidate = User(username=attrs["username"], email=attrs["email"])
        validate_django_password(attrs["password"], user=candidate)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
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
