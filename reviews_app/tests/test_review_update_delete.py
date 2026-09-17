"""Tests for updating and deleting reviews through the API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from reviews_app.models import Review
from users_app.models import Profile


User = get_user_model()
CUSTOMER = Profile.UserType.CUSTOMER
BUSINESS = Profile.UserType.BUSINESS


class ReviewUpdateDeleteTests(APITestCase):
    """Test owner permissions for changing reviews."""

    def setUp(self):
        """Create users and one existing review."""
        self.reviewer = self._create_user("reviewer", CUSTOMER)
        self.other_customer = self._create_user(
            "othercustomer",
            CUSTOMER,
        )
        self.business = self._create_user("business", BUSINESS)
        self.review = self._create_review()
        self.url = f"/api/reviews/{self.review.pk}/"

    def _create_user(self, username, profile_type):
        """Create a user with a profile."""
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

    def _create_review(self):
        """Create the review used by the tests."""
        return Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business,
            rating=4,
            description="Everything was great!",
        )

    def _authenticate(self, user):
        """Authenticate the API client as the given user."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

    def _patch(self, data):
        """Send a PATCH request to the review endpoint."""
        return self.client.patch(
            self.url,
            data,
            format="json",
        )

    def _delete(self):
        """Send a DELETE request to the review endpoint."""
        return self.client.delete(self.url)

    def test_owner_can_update_review(self):
        """Allow the reviewer to change rating and description."""
        self._authenticate(self.reviewer)
        response = self._patch(
            {
                "rating": 5,
                "description": "Even better than expected!",
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)

    def test_review_relationships_cannot_be_changed(self):
        """Keep reviewer and business user immutable."""
        self._authenticate(self.reviewer)
        response = self._patch(
            {
                "reviewer": self.other_customer.pk,
                "business_user": self.other_customer.pk,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.reviewer, self.reviewer)
        self.assertEqual(self.review.business_user, self.business)

    def test_non_owner_cannot_update_review(self):
        """Prevent another customer from updating the review."""
        self._authenticate(self.other_customer)
        response = self._patch({"rating": 2})
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_update_requires_authentication(self):
        """Reject an unauthenticated review update."""
        response = self._patch({"rating": 5})
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_rating_is_rejected_during_update(self):
        """Reject ratings outside the allowed range."""
        self._authenticate(self.reviewer)
        response = self._patch({"rating": 6})
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unknown_review_returns_not_found(self):
        """Return 404 when the review does not exist."""
        self._authenticate(self.reviewer)
        self.url = "/api/reviews/999999/"
        response = self._patch({"rating": 5})
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_can_delete_review(self):
        """Allow the reviewer to delete their review."""
        self._authenticate(self.reviewer)
        response = self._delete()
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Review.objects.filter(pk=self.review.pk).exists()
        )

    def test_non_owner_cannot_delete_review(self):
        """Prevent another customer from deleting the review."""
        self._authenticate(self.other_customer)
        response = self._delete()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_delete_requires_authentication(self):
        """Reject an unauthenticated delete request."""
        response = self._delete()
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
