"""Tests for the filtered profile list endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users_app.models import Profile


User = get_user_model()


BUSINESS_FIELDS = {
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
}

CUSTOMER_FIELDS = {
    "user",
    "username",
    "first_name",
    "last_name",
    "file",
    "uploaded_at",
    "type",
}


class ProfileListTests(APITestCase):
    """Test the filtered business and customer profile lists."""

    def setUp(self):
        """Create business and customer profiles for every test."""
        self.password = "S3cure-Pass!482"
        self.business = self._create_profile(
            "businessuser",
            Profile.UserType.BUSINESS,
        )
        self.customer = self._create_profile(
            "customeruser",
            Profile.UserType.CUSTOMER,
        )
        self.token = Token.objects.create(user=self.business.user)
        self.business_url = "/api/profiles/business/"
        self.customer_url = "/api/profiles/customer/"

    def _create_profile(self, username, profile_type):
        """Create a user and its corresponding profile."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=self.password,
        )
        return Profile.objects.create(
            user=user,
            type=profile_type,
        )

    def _authenticate(self):
        """Authenticate requests through the real token mechanism."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

    def test_business_profiles_require_authentication(self):
        response = self.client.get(self.business_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_business_endpoint_returns_only_business_profiles(self):
        self._authenticate()
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["user"],
            self.business.user_id,
        )

    def test_business_response_contains_documented_fields(self):
        self._authenticate()
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0]), BUSINESS_FIELDS)

    def test_customer_profiles_require_authentication(self):
        response = self.client.get(self.customer_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_customer_endpoint_returns_only_customer_profiles(self):
        self._authenticate()
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["user"],
            self.customer.user_id,
        )

    def test_customer_response_contains_documented_fields(self):
        self._authenticate()
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0]), CUSTOMER_FIELDS)
