"""Tests for the offer domain models."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from offers_app.models import Offer, OfferDetail


User = get_user_model()


class OfferModelTests(TestCase):
    """Test the fields and relationships of the Offer model."""

    def setUp(self):
        """Create the user who owns the test offers."""
        self.user = User.objects.create_user(
            username="businessuser",
            email="business@example.com",
            password="S3cure-Pass!482",
        )

    def _create_offer(self, title="Website Design"):
        """Create and return an offer owned by the test user."""
        return Offer.objects.create(
            user=self.user,
            title=title,
            description="Professional design service.",
        )

    def test_user_can_own_multiple_offers(self):
        """Connect multiple offers to the same user."""
        self._create_offer("Website Design")
        self._create_offer("Logo Design")

        self.assertEqual(self.user.offers.count(), 2)

    def test_offer_has_documented_fields(self):
        """Store timestamps, an optional image, and a readable name."""
        offer = self._create_offer()

        self.assertEqual(str(offer), "Website Design")
        self.assertFalse(offer.image)
        self.assertIsNotNone(offer.created_at)
        self.assertIsNotNone(offer.updated_at)

    def test_deleting_user_deletes_owned_offers(self):
        """Delete offers when their owning user is deleted."""
        self._create_offer()

        self.user.delete()

        self.assertEqual(Offer.objects.count(), 0)


class OfferDetailModelTests(TestCase):
    """Test the fields and relationships of OfferDetail."""

    def setUp(self):
        """Create the user and offer required by each test."""
        user = User.objects.create_user(
            username="businessuser",
            password="S3cure-Pass!482",
        )
        self.offer = Offer.objects.create(
            user=user,
            title="Design Package",
            description="Professional design service.",
        )

    def _create_detail(self, offer_type="basic"):
        """Create and return an offer detail."""
        return OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=Decimal("100.00"),
            features=["Logo Design", "Business Card"],
            offer_type=offer_type,
        )

    def test_offer_can_have_multiple_details(self):
        """Connect multiple details to the same offer."""
        self._create_detail("basic")
        self._create_detail("standard")

        self.assertEqual(self.offer.details.count(), 2)

    def test_detail_stores_documented_fields(self):
        """Store the documented data of an offer detail."""
        detail = self._create_detail()

        self.assertEqual(detail.price, Decimal("100.00"))
        self.assertEqual(
            detail.features,
            ["Logo Design", "Business Card"],
        )
        self.assertEqual(str(detail), "Basic Design")

    def test_offer_detail_supports_three_types(self):
        """Provide the documented basic, standard, and premium types."""
        self.assertEqual(
            set(OfferDetail.OfferType.values),
            {"basic", "standard", "premium"},
        )

    def test_deleting_offer_deletes_its_details(self):
        """Delete details when their related offer is deleted."""
        self._create_detail()

        self.offer.delete()

        self.assertEqual(OfferDetail.objects.count(), 0)
