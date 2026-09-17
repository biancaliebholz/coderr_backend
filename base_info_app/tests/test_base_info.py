"""Tests for the public base-info endpoint."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from reviews_app.models import Review
from users_app.models import Profile


User = get_user_model()


BASE_INFO_FIELDS = {
    "review_count",
    "average_rating",
    "business_profile_count",
    "offer_count",
}


class BaseInfoTests(APITestCase):
    """Test the aggregate public platform statistics."""

    def setUp(self):
        """Create users used by the aggregate tests."""
        self.url = "/api/base-info/"
        self.business = self._create_user(
            "business",
            Profile.UserType.BUSINESS,
        )
        self.customers = [
            self._create_user("customer1", Profile.UserType.CUSTOMER),
            self._create_user("customer2", Profile.UserType.CUSTOMER),
            self._create_user("customer3", Profile.UserType.CUSTOMER),
        ]

    def _create_user(self, username, profile_type):
        """Create a user with the requested profile type."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(
            user=user,
            type=profile_type,
        )
        return user

    def _create_statistics(self):
        """Create offers and reviews used for aggregation."""
        Offer.objects.create(
            user=self.business,
            title="Website Design",
            description="Professional website development.",
        )
        for reviewer, rating in zip(self.customers, [4, 5, 5]):
            Review.objects.create(
                reviewer=reviewer,
                business_user=self.business,
                rating=rating,
                description="Good service.",
            )

    def test_base_info_is_public(self):
        """Allow access without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_contains_documented_fields(self):
        """Return exactly the documented statistics."""
        response = self.client.get(self.url)
        self.assertEqual(set(response.data), BASE_INFO_FIELDS)

    def test_response_contains_correct_counts(self):
        """Return the current platform totals."""
        self._create_statistics()
        response = self.client.get(self.url)
        self.assertEqual(response.data["review_count"], 3)
        self.assertEqual(response.data["business_profile_count"], 1)
        self.assertEqual(response.data["offer_count"], 1)

    def test_average_rating_is_rounded(self):
        """Round the average rating to one decimal place."""
        self._create_statistics()
        response = self.client.get(self.url)
        self.assertEqual(response.data["average_rating"], 4.7)

    def test_empty_database_returns_zero_values(self):
        """Return zero when no offers or reviews exist."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["offer_count"], 0)
