"""Tests for the order domain model."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders_app.models import Order


User = get_user_model()


class OrderModelTests(TestCase):
    """Test the stored order snapshot and its user relationships."""

    def setUp(self):
        """Create an order shared by a customer and business user."""
        self.customer = self._create_user("customer")
        self.business = self._create_user("business")
        self.order = Order.objects.create(**self._order_data())

    def _create_user(self, username):
        """Create a user for one side of an order."""
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )

    def _order_data(self):
        """Return a complete snapshot of an ordered package."""
        return {
            "customer_user": self.customer,
            "business_user": self.business,
            "title": "Logo Design",
            "revisions": 3,
            "delivery_time_in_days": 5,
            "price": Decimal("100.00"),
            "features": ["Logo Design", "Business Card"],
            "offer_type": "basic",
        }

    def test_order_references_both_users(self):
        """Connect the order to its customer and business user."""
        self.assertEqual(self.order.customer_user, self.customer)
        self.assertEqual(self.order.business_user, self.business)
        self.assertIn(self.order, self.customer.customer_orders.all())
        self.assertIn(self.order, self.business.business_orders.all())

    def test_order_stores_package_snapshot(self):
        """Preserve the ordered package values."""
        self.assertEqual(self.order.title, "Logo Design")
        self.assertEqual(self.order.revisions, 3)
        self.assertEqual(self.order.delivery_time_in_days, 5)
        self.assertEqual(self.order.price, Decimal("100.00"))
        self.assertEqual(self.order.features, ["Logo Design", "Business Card"])
        self.assertEqual(self.order.offer_type, "basic")

    def test_new_order_defaults_to_in_progress(self):
        """Start every new order with the documented status."""
        self.assertEqual(self.order.status, "in_progress")

    def test_order_stores_timestamps(self):
        """Store creation and last-update timestamps."""
        self.assertIsNotNone(self.order.created_at)
        self.assertIsNotNone(self.order.updated_at)

    def test_order_has_readable_string_representation(self):
        """Represent an order through its title."""
        self.assertEqual(str(self.order), "Logo Design")
