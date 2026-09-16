"""Tests for the order count endpoints."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders_app.models import Order
from users_app.models import Profile


User = get_user_model()


class OrderCountTests(APITestCase):
    """Test active and completed order counts for business users."""

    def setUp(self):
        """Create users and orders with different statuses."""
        self.customer = self._create_user("customer", "customer")
        self.business = self._create_user("business", "business")
        self.other_business = self._create_user("other", "business")
        self._create_test_orders()
        self.order_count_url = self._order_count_url(self.business)
        self.completed_url = self._completed_url(self.business)

    def _create_user(self, username, profile_type):
        """Create a user with a profile and token."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(user=user, type=profile_type)
        user.token = Token.objects.create(user=user)
        return user

    def _create_test_orders(self):
        """Create orders required for the counting tests."""
        self._create_order(self.business, Order.Status.IN_PROGRESS)
        self._create_order(self.business, Order.Status.IN_PROGRESS)
        self._create_order(self.business, Order.Status.COMPLETED)
        self._create_order(self.business, Order.Status.CANCELLED)
        self._create_order(self.other_business, Order.Status.IN_PROGRESS)

    def _create_order(self, business, order_status):
        """Create one order with the selected status."""
        return Order.objects.create(
            customer_user=self.customer,
            business_user=business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=Decimal("150.00"),
            features=["Logo Design"],
            offer_type=Order.OfferType.BASIC,
            status=order_status,
        )

    def _order_count_url(self, user):
        """Return the active-order count URL for a user."""
        return f"/api/order-count/{user.pk}/"

    def _completed_url(self, user):
        """Return the completed-order count URL for a user."""
        return f"/api/completed-order-count/{user.pk}/"

    def _authenticate(self):
        """Authenticate as the customer."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.customer.token.key}"
        )

    def _assert_status_for_urls(self, urls, expected_status):
        """Assert the same response status for multiple URLs."""
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_order_count_returns_in_progress_orders(self):
        """Count only in-progress orders of the business user."""
        self._authenticate()
        response = self.client.get(self.order_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_count": 2})

    def test_completed_count_returns_completed_orders(self):
        """Count only completed orders of the business user."""
        self._authenticate()
        response = self.client.get(self.completed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {"completed_order_count": 1}
        self.assertEqual(response.data, expected)

    def test_count_endpoints_require_authentication(self):
        """Reject unauthenticated count requests."""
        urls = [self.order_count_url, self.completed_url]
        self._assert_status_for_urls(
            urls,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unknown_business_user_returns_not_found(self):
        """Return 404 when the requested user does not exist."""
        self._authenticate()
        urls = [
            "/api/order-count/999999/",
            "/api/completed-order-count/999999/",
        ]
        self._assert_status_for_urls(urls, status.HTTP_404_NOT_FOUND)

    def test_customer_id_returns_not_found(self):
        """Return 404 when the requested user is not a provider."""
        self._authenticate()
        urls = [
            self._order_count_url(self.customer),
            self._completed_url(self.customer),
        ]
        self._assert_status_for_urls(urls, status.HTTP_404_NOT_FOUND)
