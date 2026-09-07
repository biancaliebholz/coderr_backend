"""Tests for the user login endpoint."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


User = get_user_model()


class LoginTests(APITestCase):
    """Test successful and invalid user logins."""

    def setUp(self):
        self.url = "/api/login/"
        self.password = "S3cure-Pass!482"
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password=self.password,
        )

    def _login(self, data=None):
        credentials = {
            "username": self.user.username,
            "password": self.password,
        }
        payload = credentials if data is None else data
        return self.client.post(self.url, payload, format="json")

    def test_valid_login_returns_user_data_and_token(self):
        response = self._login()
        expected_fields = {"token", "username", "email", "user_id"}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), expected_fields)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["user_id"], self.user.id)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data["token"], token.key)

    def test_login_rejects_invalid_password(self):
        data = {
            "username": self.user.username,
            "password": "Wrong-Pass!123",
        }
        response = self._login(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_login_rejects_unknown_username(self):
        data = {
            "username": "unknownuser",
            "password": self.password,
        }
        response = self._login(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_login_rejects_missing_password(self):
        data = {"username": self.user.username}
        response = self._login(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_rejects_missing_username(self):
        data = {"password": self.password}
        response = self._login(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_repeated_login_reuses_token(self):
        first_response = self._login()
        second_response = self._login()
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first_response.data["token"],
            second_response.data["token"],
        )
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)
