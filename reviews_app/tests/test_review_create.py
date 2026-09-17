"""Tests for creating reviews through the API."""

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


class ReviewCreateTests(APITestCase):
    """Test the creation of customer reviews."""

    def setUp(self):
        """Create customer and business test accounts."""
        self.url = "/api/reviews/"
        self.customer = self._create_user("customer", CUSTOMER)
        self.business = self._create_user("business", BUSINESS)
        self.other_customer = self._create_user(
            "othercustomer",
            CUSTOMER,
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

    def _create_user_without_profile(self):
        """Create a user without an associated profile."""
        return User.objects.create_user(
            username="withoutprofile",
            email="withoutprofile@example.com",
            password="S3cure-Pass!482",
        )

    def _create_existing_review(self):
        """Create an existing review for duplicate validation."""
        return Review.objects.create(
            reviewer=self.customer,
            business_user=self.business,
            rating=4,
            description="First review",
        )

    def _authenticate(self, user):
        """Authenticate requests with the user's token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

    def _valid_data(self):
        """Return a valid review request body."""
        return {
            "business_user": self.business.pk,
            "rating": 4,
            "description": "Everything was great!",
        }

    def _post(self, data=None):
        """Send a review creation request."""
        payload = self._valid_data() if data is None else data
        return self.client.post(self.url, payload, format="json")

    def test_customer_can_create_review(self):
        """Allow a customer to review a business user."""
        self._authenticate(self.customer)
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.get().reviewer, self.customer)

    def test_created_review_contains_documented_fields(self):
        """Return all documented fields after creation."""
        self._authenticate(self.customer)
        response = self._post()
        self.assertEqual(set(response.data), REVIEW_FIELDS)

    def test_review_creation_requires_authentication(self):
        """Reject an unauthenticated review request."""
        response = self._post()
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_business_user_cannot_create_review(self):
        """Prevent business users from writing reviews."""
        self._authenticate(self.business)
        response = self._post()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_duplicate_review_is_rejected(self):
        """Allow one review per customer and business pair."""
        self._create_existing_review()
        self._authenticate(self.customer)
        response = self._post()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_customer_profile_cannot_be_reviewed(self):
        """Reject a customer as the review recipient."""
        self._authenticate(self.customer)
        data = self._valid_data()
        data["business_user"] = self.other_customer.pk
        response = self._post(data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_rating_is_rejected(self):
        """Reject ratings outside the range from one to five."""
        self._authenticate(self.customer)
        data = self._valid_data()
        data["rating"] = 6
        response = self._post(data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_without_profile_cannot_be_reviewed(self):
        """Reject a review recipient without a profile."""
        user = self._create_user_without_profile()
        self._authenticate(self.customer)
        data = self._valid_data()
        data["business_user"] = user.pk
        response = self._post(data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
