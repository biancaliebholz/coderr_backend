"""Tests for the user profile endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users_app.models import Profile


User = get_user_model()


PROFILE_RESPONSE_FIELDS = {
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
}


PROFILE_UPDATE_DATA = {
    "first_name": "Updated",
    "last_name": "User",
    "location": "Hamburg",
    "tel": "+49 123 456789",
    "description": "Updated business description",
    "working_hours": "10-18",
    "email": "updated@example.com",
}


class ProfileDetailTests(APITestCase):
    """Test retrieving and updating individual user profiles."""

    def setUp(self):
        self.password = "S3cure-Pass!482"
        self.user = self._create_user(
            "businessuser",
            "business@example.com",
        )
        self.profile = self._create_profile()
        self.token = Token.objects.create(user=self.user)
        self.url = f"/api/profile/{self.user.pk}/"

    def _create_user(self, username, email):
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.password,
            first_name="Max",
            last_name="Mustermann",
        )

    def _create_profile(self):
        return Profile.objects.create(
            user=self.user,
            type=Profile.UserType.BUSINESS,
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
        )

    def _create_other_user(self):
        user = self._create_user("customeruser", "customer@example.com")
        Profile.objects.create(
            user=user,
            type=Profile.UserType.CUSTOMER,
        )
        return user

    def _authenticate(self, user=None):
        authenticated_user = user or self.user
        token, _ = Token.objects.get_or_create(user=authenticated_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_authenticated_user_can_retrieve_profile(self):
        self._authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), PROFILE_RESPONSE_FIELDS)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["type"], Profile.UserType.BUSINESS)

    def test_authenticated_user_can_retrieve_another_profile(self):
        other_user = self._create_other_user()
        self._authenticate(other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_retrieve_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_missing_profile_returns_not_found(self):
        self._authenticate()
        response = self.client.get("/api/profile/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_update_profile(self):
        self._authenticate()
        response = self.client.patch(
            self.url,
            PROFILE_UPDATE_DATA,
            format="json",
        )
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field, value in PROFILE_UPDATE_DATA.items():
            self.assertEqual(response.data[field], value)
        self.assertEqual(self.user.email, PROFILE_UPDATE_DATA["email"])
        self.assertEqual(self.profile.location, PROFILE_UPDATE_DATA["location"])

    def test_unauthenticated_user_cannot_update_profile(self):
        response = self.client.patch(
            self.url,
            {"location": "Hamburg"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_cannot_update_another_profile(self):
        other_user = self._create_other_user()
        self._authenticate(other_user)
        response = self.client.patch(
            self.url,
            {"location": "Hamburg"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_profile_update_returns_not_found(self):
        self._authenticate()
        response = self.client.patch(
            "/api/profile/999999/",
            {"location": "Hamburg"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_rejects_invalid_email(self):
        self._authenticate()
        response = self.client.patch(
            self.url,
            {"email": "not-an-email"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_update_does_not_change_profile_type(self):
        self._authenticate()
        response = self.client.patch(
            self.url,
            {"type": Profile.UserType.CUSTOMER},
            format="json",
        )
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.type, Profile.UserType.BUSINESS)
