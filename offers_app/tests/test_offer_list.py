"""Tests for listing offers through the API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.api.serializers import (
    OfferDetailReferenceSerializer,
)
from offers_app.models import Offer, OfferDetail
from users_app.models import Profile


User = get_user_model()


OFFER_LIST_FIELDS = {
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
    "user_details",
}


class OfferListTests(APITestCase):
    """Test the public paginated offer list."""

    def setUp(self):
        """Create one business offer with three package details."""
        self.url = "/api/offers/"
        self.business = self._create_business_user()
        self.offer = Offer.objects.create(
            user=self.business,
            title="Website Design",
            description="Professional website development.",
        )
        self._create_offer_details()

    def _create_business_user(self):
        """Create a user with a business profile."""
        user = User.objects.create_user(
            username="businessuser",
            first_name="John",
            last_name="Doe",
            email="business@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(
            user=user,
            type=Profile.UserType.BUSINESS,
        )
        return user

    def _create_offer_details(self):
        """Create the three documented package types."""
        self._create_detail("basic", 100, 5)
        self._create_detail("standard", 200, 7)
        self._create_detail("premium", 500, 10)

    def _create_detail(self, offer_type, price, delivery_time):
        """Create one package belonging to the test offer."""
        return OfferDetail.objects.create(
            offer=self.offer,
            title=f"{offer_type.title()} Design",
            revisions=2,
            delivery_time_in_days=delivery_time,
            price=price,
            features=["Logo Design"],
            offer_type=offer_type,
        )

    def _get_successful_response(self):
        """Request the list and verify its documented status."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        return response

    def _first_result(self):
        """Return the first offer from the paginated response."""
        response = self._get_successful_response()
        return response.data["results"][0]

    def test_offer_list_is_public_and_paginated(self):
        """Return a paginated list without authentication."""
        response = self._get_successful_response()
        expected_keys = {
            "count",
            "next",
            "previous",
            "results",
        }
        self.assertEqual(set(response.data), expected_keys)
        self.assertEqual(response.data["count"], 1)

    def test_offer_list_contains_documented_fields(self):
        """Return all documented fields for every offer."""
        result = self._first_result()
        self.assertEqual(set(result), OFFER_LIST_FIELDS)

    def test_offer_list_contains_calculated_minimum_values(self):
        """Return the cheapest price and shortest delivery time."""
        result = self._first_result()
        self.assertEqual(float(result["min_price"]), 100.0)
        self.assertEqual(result["min_delivery_time"], 5)

    def test_offer_list_contains_creator_details(self):
        """Return the documented public data of the creator."""
        result = self._first_result()
        expected = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "businessuser",
        }
        self.assertEqual(result["user_details"], expected)

    def test_offer_list_contains_detail_links(self):
        """Represent details through their IDs and URLs."""
        result = self._first_result()
        self.assertEqual(len(result["details"]), 3)
        self.assertEqual(
            set(result["details"][0]),
            {"id", "url"},
        )

    def test_detail_reference_uses_relative_url_without_request(self):
        """Return a relative detail URL without request context."""
        detail = self.offer.details.first()
        serializer = OfferDetailReferenceSerializer(detail)
        expected_url = f"/api/offerdetails/{detail.pk}/"
        self.assertEqual(serializer.data["url"], expected_url)
