"""Tests for deleting orders through the API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders_app.models import Order


User = get_user_model()


class OrderDeleteTests(APITestCase):
    """Test that only staff users can delete orders."""

    def setUp(self):
        """Create users, tokens, and one order."""
        self.customer = self._create_user("customer")
        self.business = self._create_user("business")
        self.staff = self._create_user("staff", is_staff=True)
        self.order = self._create_order()
        self.url = f"/api/orders/{self.order.pk}/"

    def _create_user(self, username, is_staff=False):
        """Create a user and authentication token."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
            is_staff=is_staff,
        )
        user.token = Token.objects.create(user=user)
        return user

    def _create_order(self):
        """Create an order used by the deletion tests."""
        return Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=Decimal("150.00"),
            features=["Logo Design"],
            offer_type=Order.OfferType.BASIC,
        )

    def _authenticate(self, user):
        """Authenticate the API client with the user's token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {user.token.key}"
        )

    def test_staff_user_can_delete_order(self):
        """Allow a staff user to delete an order."""
        self._authenticate(self.staff)
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_customer_cannot_delete_order(self):
        """Prevent a regular customer from deleting an order."""
        self._authenticate(self.customer)
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_business_user_cannot_delete_order(self):
        """Prevent a regular provider from deleting an order."""
        self._authenticate(self.business)
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_order_deletion_requires_authentication(self):
        """Reject an unauthenticated deletion request."""
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unknown_order_returns_not_found(self):
        """Return 404 when the requested order does not exist."""
        self._authenticate(self.staff)
        response = self.client.delete("/api/orders/999999/")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
