"""Tests for retrieving one offer through the API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer


User = get_user_model()


class OfferDetailTests(APITestCase):
    """Test access to one specific offer."""

    def setUp(self):
        """Create an offer for the detail tests."""
        self.user = User.objects.create_user(
            username="businessuser",
            email="business@example.com",
            password="S3cure-Pass!482",
        )
        self.offer = Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professional website development.",
        )
        self.url = f"/api/offers/{self.offer.pk}/"

    def test_offer_detail_requires_authentication(self):
        """Reject access to an offer without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
