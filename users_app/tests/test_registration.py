from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users_app.models import Profile


User = get_user_model()


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = "/api/registration/"
        self.data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "S3cure-Pass!482",
            "repeated_password": "S3cure-Pass!482",
            "type": "customer",
        }

    def register_user(self, data=None):
        return self.client.post(self.url, data or self.data, format="json")

    def test_valid_registration_creates_user(self):
        response = self.register_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_registration_returns_expected_data(self):
        response = self.register_user()
        user = User.objects.get(username="testuser")
        token = Token.objects.get(user=user)
        expected = {"token", "username", "email", "user_id"}
        self.assertEqual(set(response.data), expected)
        self.assertEqual(response.data["token"], token.key)
        self.assertEqual(response.data["user_id"], user.id)

    def test_registration_creates_customer_profile(self):
        self.register_user()
        user = User.objects.get(username="testuser")
        self.assertEqual(user.profile.type, Profile.UserType.CUSTOMER)

    def test_registration_hashes_password(self):
        self.register_user()
        user = User.objects.get(username="testuser")
        self.assertNotEqual(user.password, self.data["password"])
        self.assertTrue(user.check_password(self.data["password"]))

    def test_registration_rejects_mismatched_passwords(self):
        data = {**self.data, "repeated_password": "Different-Pass!482"}
        response = self.register_user(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_registration_rejects_invalid_type(self):
        data = {**self.data, "type": "invalid"}
        response = self.register_user(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)

    def test_registration_rejects_weak_password(self):
        data = {**self.data, "password": "123", "repeated_password": "123"}
        response = self.register_user(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_rejects_duplicate_email(self):
        self.register_user()
        data = {**self.data, "username": "otheruser"}
        response = self.register_user(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_rejects_duplicate_username(self):
        self.register_user()
        data = {**self.data, "email": "other@example.com"}
        response = self.register_user(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
