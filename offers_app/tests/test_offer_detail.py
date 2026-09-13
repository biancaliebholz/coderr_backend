"""Tests for retrieving offers and individual offer details."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from users_app.models import Profile


User = get_user_model()


OFFER_FIELDS = {
    "id",
    "user",
    "title",
    "image",
    "description",
    "created_at",
    "updated_at",
    "details",
    "min_price",
    "min_delivery_time",
}


OFFER_DETAIL_FIELDS = {
    "id",
    "title",
    "revisions",
    "delivery_time_in_days",
    "price",
    "features",
    "offer_type",
}


class OfferDetailTests(APITestCase):
    """Test the two documented offer detail endpoints."""

    def setUp(self):
        """Create a business offer with three package details."""
        self.user = self._create_business_user()
        self.offer = Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professional website development.",
        )
        self.details = self._create_offer_details()
        self.offer_url = f"/api/offers/{self.offer.pk}/"

    def _create_business_user(self):
        """Create a user with a business profile."""
        user = User.objects.create_user(
            username="businessuser",
            email="business@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(
            user=user,
            type=Profile.UserType.BUSINESS,
        )
        return user

    def _create_offer_details(self):
        """Create basic, standard, and premium details."""
        packages = [
            ("basic", 100, 5),
            ("standard", 200, 7),
            ("premium", 500, 10),
        ]
        return [
            self._create_detail(*package)
            for package in packages
        ]

    def _create_detail(self, offer_type, price, delivery_time):
        """Create one package belonging to the offer."""
        return OfferDetail.objects.create(
            offer=self.offer,
            title=f"{offer_type.title()} Design",
            revisions=2,
            delivery_time_in_days=delivery_time,
            price=price,
            features=["Logo Design"],
            offer_type=offer_type,
        )

    def _authenticate(self):
        """Authenticate the client as the offer owner."""
        self.client.force_authenticate(user=self.user)

    def _get_offer_response(self):
        """Retrieve the offer and verify a successful response."""
        self._authenticate()
        response = self.client.get(self.offer_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        return response

    def _get_detail_response(self):
        """Retrieve one package and verify a successful response."""
        self._authenticate()
        url = f"/api/offerdetails/{self.details[0].pk}/"
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        return response

    def test_offer_requires_authentication(self):
        """Reject offer retrieval without authentication."""
        response = self.client.get(self.offer_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_retrieve_offer(self):
        """Allow an authenticated user to retrieve an offer."""
        response = self._get_offer_response()
        self.assertEqual(response.data["id"], self.offer.id)

    def test_offer_response_contains_documented_fields(self):
        """Return exactly the documented offer fields."""
        response = self._get_offer_response()
        self.assertEqual(set(response.data), OFFER_FIELDS)

    def test_offer_contains_calculated_minimum_values(self):
        """Return the lowest price and delivery time."""
        response = self._get_offer_response()
        self.assertEqual(float(response.data["min_price"]), 100.0)
        self.assertEqual(response.data["min_delivery_time"], 5)

    def test_offer_contains_detail_references(self):
        """Return IDs and URLs for the related details."""
        response = self._get_offer_response()
        detail = response.data["details"][0]
        self.assertEqual(set(detail), {"id", "url"})
        self.assertIn("/api/offerdetails/", detail["url"])

    def test_unknown_offer_returns_not_found(self):
        """Return 404 when an offer does not exist."""
        self._authenticate()
        response = self.client.get("/api/offers/999999/")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_offer_detail_requires_authentication(self):
        """Reject package retrieval without authentication."""
        url = f"/api/offerdetails/{self.details[0].pk}/"
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_retrieve_offer_detail(self):
        """Allow an authenticated user to retrieve one package."""
        response = self._get_detail_response()
        self.assertEqual(response.data["id"], self.details[0].id)

    def test_offer_detail_contains_documented_fields(self):
        """Return exactly the documented package fields."""
        response = self._get_detail_response()
        self.assertEqual(
            set(response.data),
            OFFER_DETAIL_FIELDS,
        )

    def test_unknown_offer_detail_returns_not_found(self):
        """Return 404 when an offer detail does not exist."""
        self._authenticate()
        response = self.client.get(
            "/api/offerdetails/999999/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
