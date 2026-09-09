from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Represent a user who can authenticate with the Coderr API."""


class Profile(models.Model):
    """Store the role and additional public data of a Coderr user."""

    class UserType(models.TextChoices):
        """Define the supported profile roles."""

        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    type = models.CharField(
        max_length=8,
        choices=UserType.choices,
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    tel = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )

    description = models.TextField(
        max_length=500,
        blank=True,
        default="",
    )

    working_hours = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    file = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        """Return a readable representation of the profile."""
        return f"{self.user.username} ({self.get_type_display()})"
