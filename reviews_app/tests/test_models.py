"""Tests for the review domain model."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from reviews_app.models import Review
from users_app.models import Profile


User = get_user_model()


class ReviewModelTests(TestCase):
    """Test relationships, validation, and constraints of reviews."""

    def setUp(self):
        """Create users and one valid review."""
        self.reviewer = self._create_user(
            "customer",
            Profile.UserType.CUSTOMER,
        )
        self.business = self._create_user(
            "business",
            Profile.UserType.BUSINESS,
        )
        self.review = self._create_review()

    def _create_user(self, username, profile_type):
        """Create a user with the requested profile type."""
        user = User.objects.create_user(
            username=username,
            password="S3cure-Pass!482",
        )
        Profile.objects.create(user=user, type=profile_type)
        return user

    def _create_review(self):
        """Create a valid review between the test users."""
        return Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business,
            rating=4,
            description="Very professional service.",
        )

    def test_review_stores_documented_fields(self):
        """Store users, rating, description, and timestamps."""
        self.assertEqual(self.review.reviewer, self.reviewer)
        self.assertEqual(self.review.business_user, self.business)
        self.assertEqual(self.review.rating, 4)
        self.assertTrue(self.review.created_at)
        self.assertTrue(self.review.updated_at)

    def test_review_has_readable_representation(self):
        """Return a readable description of the review."""
        expected = "customer -> business (4)"
        self.assertEqual(str(self.review), expected)

    def test_users_have_review_relationships(self):
        """Expose written and received reviews through related names."""
        self.assertIn(
            self.review,
            self.reviewer.written_reviews.all(),
        )
        self.assertIn(
            self.review,
            self.business.received_reviews.all(),
        )

    def test_reviewer_can_review_business_only_once(self):
        """Prevent duplicate reviews for the same business user."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_review()

    def test_rating_must_be_between_one_and_five(self):
        """Reject ratings outside the supported range."""
        for rating in (0, 6):
            with self.subTest(rating=rating):
                self.review.rating = rating
                with self.assertRaises(ValidationError):
                    self.review.full_clean()
