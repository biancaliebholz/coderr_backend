"""Tests for listing and filtering reviews through the API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from reviews_app.models import Review
from users_app.models import Profile


User = get_user_model()
CUSTOMER = Profile.UserType.CUSTOMER
BUSINESS = Profile.UserType.BUSINESS


REVIEW_FIELDS = {
    "id",
    "business_user",
    "reviewer",
    "rating",
    "description",
    "created_at",
    "updated_at",
}


class ReviewListTests(APITestCase):
    """Test authentication, fields, filters, and ordering."""

    def setUp(self):
        """Create users, profiles, reviews, and authentication."""
        self.url = "/api/reviews/"
        self._create_users()
        self._create_reviews()
        self.token = Token.objects.create(user=self.reviewer_one)

    def _create_users(self):
        """Create two customers and two business users."""
        self.reviewer_one = self._create_user("customer1", CUSTOMER)
        self.reviewer_two = self._create_user("customer2", CUSTOMER)
        self.business_one = self._create_user("business1", BUSINESS)
        self.business_two = self._create_user("business2", BUSINESS)

    def _create_user(self, username, profile_type):
        """Create a user with the requested profile type."""
        user = User.objects.create_user(
            username=username,
            password="S3cure-Pass!482",
        )
        Profile.objects.create(
            user=user,
            type=profile_type,
        )
        return user

    def _create_reviews(self):
        """Create reviews with different users and ratings."""
        review_data = [
            (self.reviewer_one, self.business_one, 3),
            (self.reviewer_two, self.business_one, 5),
            (self.reviewer_one, self.business_two, 4),
        ]
        reviews = [
            self._create_review(*data)
            for data in review_data
        ]
        self.review_one, self.review_two, self.review_three = reviews

    def _create_review(self, reviewer, business_user, rating):
        """Create one review for the supplied users."""
        return Review.objects.create(
            reviewer=reviewer,
            business_user=business_user,
            rating=rating,
            description=f"Rating: {rating}",
        )

    def _authenticate(self):
        """Authenticate requests with a real user token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )

    def _get_successful_response(self, parameters=None):
        """Request reviews and verify the successful status."""
        self._authenticate()
        response = self.client.get(self.url, parameters or {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_review_list_requires_authentication(self):
        """Reject unauthenticated requests."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_list_reviews(self):
        """Return every review to an authenticated user."""
        response = self._get_successful_response()
        self.assertEqual(len(response.data), 3)

    def test_review_list_contains_documented_fields(self):
        """Return exactly the documented review fields."""
        response = self._get_successful_response()
        self.assertEqual(set(response.data[0]), REVIEW_FIELDS)

    def test_reviews_can_be_filtered_by_business_user(self):
        """Return reviews belonging to one business user."""
        parameters = {"business_user_id": self.business_one.id}
        response = self._get_successful_response(parameters)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(self._all_target_business(response))

    def _all_target_business(self, response):
        """Check that every result targets business one."""
        return all(
            item["business_user"] == self.business_one.id
            for item in response.data
        )

    def test_reviews_can_be_filtered_by_reviewer(self):
        """Return reviews written by one reviewer."""
        parameters = {"reviewer_id": self.reviewer_one.id}
        response = self._get_successful_response(parameters)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(self._all_written_by_reviewer(response))

    def _all_written_by_reviewer(self, response):
        """Check that every result belongs to reviewer one."""
        return all(
            item["reviewer"] == self.reviewer_one.id
            for item in response.data
        )

    def test_reviews_can_be_ordered_by_rating(self):
        """Order reviews through the documented rating field."""
        response = self._get_successful_response(
            {"ordering": "-rating"},
        )
        ratings = [item["rating"] for item in response.data]
        self.assertEqual(ratings, [5, 4, 3])
