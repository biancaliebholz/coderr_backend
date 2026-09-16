"""Database model for customer orders."""

from django.conf import settings
from django.db import models


class Order(models.Model):
    """Store an immutable snapshot of an ordered offer package."""

    class Status(models.TextChoices):
        """Define the supported order states."""

        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class OfferType(models.TextChoices):
        """Define the supported package types."""

        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_orders",
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_orders",
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=10,
        choices=OfferType.choices,
    )
    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return the title of the ordered package."""
        return self.title
