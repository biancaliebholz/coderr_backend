"""Tests for listing orders through the API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders_app.models import Order


User = get_user_model()


ORDER_FIELDS = {
    "id",
    "customer_user",
    "business_user",
    "title",
    "revisions",
    "delivery_time_in_days",
    "price",
    "features",
    "offer_type",
    "status",
    "created_at",
    "updated_at",
}


class OrderListTests(APITestCase):
    """Test listing only orders related to the current user."""

    def setUp(self):
        """Create one visible and one unrelated order."""
        self.url = "/api/orders/"
        self.customer = self._create_user("customer")
        self.business = self._create_user("business")
        self.other_customer = self._create_user("other_customer")
        self.other_business = self._create_user("other_business")
        self.order = self._create_order(self.customer, self.business)
        self._create_order(self.other_customer, self.other_business)

    def _create_user(self, username):
        """Create a user and authentication token."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )
        user.token = Token.objects.create(user=user)
        return user

    def _create_order(self, customer, business):
        """Create a complete order snapshot."""
        return Order.objects.create(
            customer_user=customer,
            business_user=business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=Decimal("100.00"),
            features=["Logo Design"],
            offer_type="basic",
        )

    def _get_as(self, user):
        """Request the order list as the given user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {user.token.key}",
        )
        return self.client.get(self.url)

    def test_order_list_requires_authentication(self):
        """Reject unauthenticated list requests."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_customer_sees_only_own_orders(self):
        """Return orders belonging to the authenticated customer."""
        response = self._get_as(self.customer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.pk)

    def test_business_user_sees_only_own_orders(self):
        """Return orders belonging to the authenticated provider."""
        response = self._get_as(self.business)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.pk)

    def test_order_list_contains_documented_fields(self):
        """Return every documented field of an order."""
        response = self._get_as(self.customer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0]), ORDER_FIELDS)
