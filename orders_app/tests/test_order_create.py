"""Tests for creating orders through the API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from users_app.models import Profile


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


class OrderCreateTests(APITestCase):
    """Test creating an order from an offer detail."""

    def setUp(self):
        """Create customer, business user, offer and package."""
        self.url = "/api/orders/"
        self.customer = self._create_user("customer")
        self.business = self._create_user("business")
        self.detail = self._create_offer_detail()
        self.customer_token = Token.objects.create(user=self.customer)
        self.business_token = Token.objects.create(user=self.business)

    def _create_user(self, profile_type):
        """Create a user with the requested profile type."""
        user = User.objects.create_user(
            username=f"{profile_type}user",
            email=f"{profile_type}@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(user=user, type=profile_type)
        return user

    def _create_offer_detail(self):
        """Create a package that can be ordered."""
        offer = Offer.objects.create(
            user=self.business,
            title="Logo Package",
            description="Professional logo design.",
        )
        return OfferDetail.objects.create(
            offer=offer,
            title="Basic Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=Decimal("100.00"),
            features=["Logo Design", "Business Card"],
            offer_type="basic",
        )

    def _authenticate(self, token):
        """Authenticate the next request with a token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

    def _post_order(self):
        """Submit the documented order request."""
        data = {"offer_detail_id": self.detail.pk}
        return self.client.post(self.url, data, format="json")

    def test_customer_can_create_order(self):
        """Allow a customer to order an offer detail."""
        self._authenticate(self.customer_token)
        response = self._post_order()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_order_contains_documented_fields(self):
        """Return all documented order fields."""
        self._authenticate(self.customer_token)
        response = self._post_order()
        self.assertEqual(set(response.data), ORDER_FIELDS)

    def test_order_copies_package_snapshot(self):
        """Copy package data instead of storing changing offer data."""
        self._authenticate(self.customer_token)
        response = self._post_order()
        order = Order.objects.get()
        self.assertEqual(order.customer_user, self.customer)
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.title, self.detail.title)
        self.assertEqual(response.data["status"], "in_progress")

    def test_unauthenticated_user_cannot_create_order(self):
        """Reject order creation without authentication."""
        response = self._post_order()
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_business_user_cannot_create_order(self):
        """Only customer profiles may create orders."""
        self._authenticate(self.business_token)
        response = self._post_order()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_missing_offer_detail_id_is_invalid(self):
        """Reject a request without an offer detail ID."""
        self._authenticate(self.customer_token)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unknown_offer_detail_returns_not_found(self):
        """Return 404 when the selected package does not exist."""
        self._authenticate(self.customer_token)
        data = {"offer_detail_id": 999999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
