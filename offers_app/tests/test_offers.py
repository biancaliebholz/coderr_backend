"""Tests for creating offers through the API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from users_app.models import Profile


User = get_user_model()


class OfferCreateTests(APITestCase):
    """Test creation and validation of offers."""

    def setUp(self):
        """Create customer and business users for the tests."""
        self.url = "/api/offers/"
        self.business = self._create_user(
            "businessuser",
            Profile.UserType.BUSINESS,
        )
        self.customer = self._create_user(
            "customeruser",
            Profile.UserType.CUSTOMER,
        )

    def _create_user(self, username, profile_type):
        """Create a user with the requested profile type."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(user=user, type=profile_type)
        return user

    def _authenticate(self, user):
        """Authenticate the API client as the provided user."""
        self.client.force_authenticate(user=user)

    def _detail(self, offer_type, price):
        """Return valid data for one offer detail."""
        return {
            "title": f"{offer_type.title()} Design",
            "revisions": 2,
            "delivery_time_in_days": 5,
            "price": price,
            "features": ["Logo Design", "Business Card"],
            "offer_type": offer_type,
        }

    def _payload(self):
        """Return a valid offer with three package types."""
        return {
            "title": "Design Package",
            "image": None,
            "description": "Professional design service.",
            "details": [
                self._detail("basic", 100),
                self._detail("standard", 200),
                self._detail("premium", 500),
            ],
        }

    def test_business_user_can_create_offer(self):
        """Allow a business user to create an offer."""
        self._authenticate(self.business)

        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_created_offer_belongs_to_authenticated_user(self):
        """Use the authenticated business user as offer owner."""
        self._authenticate(self.business)

        self.client.post(self.url, self._payload(), format="json")
        offer = Offer.objects.get()

        self.assertEqual(offer.user, self.business)

    def test_response_contains_created_detail_ids(self):
        """Return database IDs for all created offer details."""
        self._authenticate(self.business)

        response = self.client.post(self.url, self._payload(), format="json")
        detail_ids = [detail["id"] for detail in response.data["details"]]

        self.assertEqual(len(detail_ids), 3)
        self.assertTrue(all(detail_ids))

    def test_unauthenticated_user_cannot_create_offer(self):
        """Reject offer creation without authentication."""
        response = self.client.post(
            self.url,
            self._payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_customer_cannot_create_offer(self):
        """Reject offer creation by a customer user."""
        self._authenticate(self.customer)

        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_requires_exactly_three_details(self):
        """Reject an offer without exactly three details."""
        self._authenticate(self.business)
        payload = self._payload()
        payload["details"] = payload["details"][:2]

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_requires_each_package_type(self):
        """Require basic, standard, and premium details."""
        self._authenticate(self.business)
        payload = self._payload()
        payload["details"][2]["offer_type"] = "standard"

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
