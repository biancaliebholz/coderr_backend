from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Represent a customer's review of a business user."""

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews",
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )
    description = models.TextField(
        max_length=500,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        """Define ordering and database constraints."""

        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "business_user"],
                name="unique_reviewer_business_review",
            ),
        ]

    def __str__(self):
        """Return a readable representation of the review."""
        return (
            f"{self.reviewer.username} -> "
            f"{self.business_user.username} ({self.rating})"
        )
