"""Tests for updating order statuses through the API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders_app.models import Order
from users_app.models import Profile


User = get_user_model()


class OrderUpdateTests(APITestCase):
    """Test the protected order status update endpoint."""

    def setUp(self):
        """Create an order and its participating users."""
        self.customer = self._create_user("customer", "customer")
        self.business = self._create_user("business", "business")
        self.other_business = self._create_user(
            "other_business",
            "business",
        )
        self.order = self._create_order()
        self.url = f"/api/orders/{self.order.pk}/"

    def _create_user(self, username, profile_type):
        """Create a user, profile and authentication token."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(user=user, type=profile_type)
        user.token = Token.objects.create(user=user)
        return user

    def _create_order(self):
        """Create an order that can be updated."""
        return Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=Decimal("100.00"),
            features=["Logo Design"],
            offer_type="basic",
        )

    def _patch_as(self, user, data):
        """Update the order as the supplied user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {user.token.key}",
        )
        return self.client.patch(self.url, data, format="json")

    def test_assigned_business_user_can_update_status(self):
        """Allow the assigned provider to complete an order."""
        response = self._patch_as(
            self.business,
            {"status": "completed"},
        )
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, "completed")
        self.assertEqual(response.data["status"], "completed")

    def test_customer_cannot_update_status(self):
        """Prevent the customer from changing the order status."""
        response = self._patch_as(
            self.customer,
            {"status": "completed"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unrelated_business_cannot_update_status(self):
        """Prevent another provider from changing the order."""
        response = self._patch_as(
            self.other_business,
            {"status": "completed"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_status_update_requires_authentication(self):
        """Reject an unauthenticated status update."""
        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_status_is_rejected(self):
        """Reject a status outside the model choices."""
        response = self._patch_as(
            self.business,
            {"status": "unknown"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unknown_order_returns_not_found(self):
        """Return 404 when the requested order does not exist."""
        self.url = "/api/orders/999999/"
        response = self._patch_as(
            self.business,
            {"status": "completed"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_snapshot_fields_cannot_be_changed(self):
        """Keep purchased package data immutable."""
        response = self._patch_as(
            self.business,
            {"status": "completed", "title": "Changed"},
        )
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.title, "Logo Design")
