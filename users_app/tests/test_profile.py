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
        """Create a business user, profile, token, and endpoint URL."""
        self.password = "S3cure-Pass!482"
        self.user = self._create_user(
            "businessuser",
            "business@example.com",
        )
        self.profile = self._create_profile()
        self.token = Token.objects.create(user=self.user)
        self.url = f"/api/profile/{self.user.pk}/"

    def _create_user(self, username, email):
        """Create and return a user with valid login credentials."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.password,
            first_name="Max",
            last_name="Mustermann",
        )

    def _create_profile(self):
        """Create and return the business profile used in the tests."""
        return Profile.objects.create(
            user=self.user,
            type=Profile.UserType.BUSINESS,
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
        )

    def _create_other_user(self):
        """Create a second user with a customer profile."""
        user = self._create_user(
            "customeruser",
            "customer@example.com",
        )
        Profile.objects.create(
            user=user,
            type=Profile.UserType.CUSTOMER,
        )
        return user

    def _authenticate(self, user=None):
        """Authenticate API requests using the selected user's token."""
        authenticated_user = user or self.user
        token, _ = Token.objects.get_or_create(user=authenticated_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def _assert_profile_was_updated(self, response):
        """Assert that response, user, and profile contain new values."""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field, value in PROFILE_UPDATE_DATA.items():
            self.assertEqual(response.data[field], value)
        self.assertEqual(
            self.user.email,
            PROFILE_UPDATE_DATA["email"],
        )
        self.assertEqual(
            self.profile.location,
            PROFILE_UPDATE_DATA["location"],
        )

    def test_authenticated_user_can_retrieve_profile(self):
        """Allow an authenticated user to retrieve a profile."""
        self._authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), PROFILE_RESPONSE_FIELDS)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(
            response.data["type"],
            Profile.UserType.BUSINESS,
        )

    def test_authenticated_user_can_retrieve_another_profile(self):
        """Allow an authenticated user to retrieve another profile."""
        other_user = self._create_other_user()
        self._authenticate(other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_retrieve_profile(self):
        """Reject profile retrieval without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_missing_profile_returns_not_found(self):
        """Return 404 when the requested profile does not exist."""
        self._authenticate()
        response = self.client.get("/api/profile/999999/")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_can_update_profile(self):
        """Allow the owner to update profile and related user fields."""
        self._authenticate()
        response = self.client.patch(
            self.url,
            PROFILE_UPDATE_DATA,
            format="json",
        )
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self._assert_profile_was_updated(response)

    def test_unauthenticated_user_cannot_update_profile(self):
        """Reject profile updates without authentication."""
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
        """Prevent a user from updating another user's profile."""
        other_user = self._create_other_user()
        self._authenticate(other_user)
        response = self.client.patch(
            self.url,
            {"location": "Hamburg"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_missing_profile_update_returns_not_found(self):
        """Return 404 when updating a profile that does not exist."""
        self._authenticate()
        response = self.client.patch(
            "/api/profile/999999/",
            {"location": "Hamburg"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_rejects_invalid_email(self):
        """Reject an incorrectly formatted email address."""
        self._authenticate()
        response = self.client.patch(
            self.url,
            {"email": "not-an-email"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("email", response.data)

    def test_update_does_not_change_profile_type(self):
        """Ignore attempts to change the read-only profile type."""
        self._authenticate()
        response = self.client.patch(
            self.url,
            {"type": Profile.UserType.CUSTOMER},
            format="json",
        )
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.type, Profile.UserType.BUSINESS)

    def test_update_rejects_email_used_by_another_user(self):
        """Reject an email address belonging to another user."""
        other_user = self._create_other_user()
        self._authenticate()
        response = self.client.patch(
            self.url,
            {"email": other_user.email},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("email", response.data)

    def test_profile_has_readable_string_representation(self):
        """Return the username and readable profile type."""
        expected = "businessuser (Business)"
        self.assertEqual(str(self.profile), expected)
