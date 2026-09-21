"""Tests for updating and deleting offers through the API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from users_app.models import Profile


User = get_user_model()


class OfferUpdateDeleteTests(APITestCase):
    """Test offer updates, nested detail updates, and deletion."""

    def setUp(self):
        """Create owners, offers, and their package details."""
        self.owner = self._create_business_user("owner")
        self.other = self._create_business_user("other")
        self.offer = self._create_offer(self.owner, "Original Offer")
        self.basic = self._create_detail(
            self.offer,
            "basic",
            Decimal("100.00"),
        )
        self._create_detail(
            self.offer,
            "standard",
            Decimal("200.00"),
        )
        self._create_detail(
            self.offer,
            "premium",
            Decimal("300.00"),
        )
        foreign_offer = self._create_offer(self.other, "Foreign Offer")
        self.foreign_detail = self._create_detail(
            foreign_offer,
            "basic",
            Decimal("400.00"),
        )
        self.url = f"/api/offers/{self.offer.pk}/"

    def _create_business_user(self, username):
        """Create a user with a business profile."""
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="S3cure-Pass!482",
        )
        Profile.objects.create(
            user=user,
            type=Profile.UserType.BUSINESS,
        )
        return user

    def _create_offer(self, user, title):
        """Create an offer belonging to the supplied user."""
        return Offer.objects.create(
            user=user,
            title=title,
            description="Offer description.",
        )

    def _create_detail(self, offer, offer_type, price):
        """Create one package belonging to an offer."""
        return OfferDetail.objects.create(
            offer=offer,
            title=f"{offer_type.title()} Package",
            revisions=2,
            delivery_time_in_days=5,
            price=price,
            features=["Feature"],
            offer_type=offer_type,
        )

    def _authenticate(self, user):
        """Authenticate subsequent requests as the supplied user."""
        self.client.force_authenticate(user=user)

    def _patch_as(self, user, data):
        """Send an authenticated partial update."""
        self._authenticate(user)
        return self.client.patch(
            self.url,
            data,
            format="json",
        )

    def _delete_as(self, user):
        """Send an authenticated delete request."""
        self._authenticate(user)
        return self.client.delete(self.url)

    def _updated_detail_data(self):
        """Return valid update data for the basic package."""
        return {
            "id": self.basic.pk,
            "title": "Updated Basic Package",
            "revisions": 3,
            "delivery_time_in_days": 6,
            "price": "120.00",
            "features": ["Updated Feature"],
            "offer_type": "basic",
        }

    def test_owner_can_update_offer_title(self):
        """Allow the creator to update the offer."""
        response = self._patch_as(
            self.owner,
            {"title": "Updated Offer"},
        )
        self.offer.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.offer.title, "Updated Offer")

    def test_owner_can_update_one_offer_detail(self):
        """Allow nested updates using a detail ID."""
        detail_data = self._updated_detail_data()
        response = self._patch_as(
            self.owner,
            {"details": [detail_data]},
        )
        self.basic.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic.title, detail_data["title"])

    def test_detail_update_does_not_require_id(self):
        """Identify a detail through its type when ID is omitted."""
        detail_data = self._updated_detail_data()
        detail_data.pop("id")
        response = self._patch_as(
            self.owner,
            {"details": [detail_data]},
        )
        self.basic.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.basic.title,
            detail_data["title"],
        )

    def test_detail_update_requires_offer_type(self):
        """Reject a nested update without its package type."""
        detail_data = self._updated_detail_data()
        detail_data.pop("offer_type")
        response = self._patch_as(
            self.owner,
            {"details": [detail_data]},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_update_detail_from_another_offer(self):
        """Reject an ID belonging to another offer."""
        detail_data = self._updated_detail_data()
        detail_data["id"] = self.foreign_detail.pk
        response = self._patch_as(
            self.owner,
            {"details": [detail_data]},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_other_user_cannot_update_offer(self):
        """Prevent another user from updating the offer."""
        response = self._patch_as(
            self.other,
            {"title": "Forbidden Update"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_update_offer(self):
        """Reject an unauthenticated update."""
        response = self.client.patch(
            self.url,
            {"title": "Forbidden Update"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_owner_can_delete_offer(self):
        """Allow the creator to delete the offer."""
        response = self._delete_as(self.owner)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Offer.objects.filter(pk=self.offer.pk).exists()
        )

    def test_other_user_cannot_delete_offer(self):
        """Prevent another user from deleting the offer."""
        response = self._delete_as(self.other)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Offer.objects.filter(pk=self.offer.pk).exists()
        )

    def test_unauthenticated_user_cannot_delete_offer(self):
        """Reject an unauthenticated delete request."""
        response = self.client.delete(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unknown_offer_returns_not_found(self):
        """Return 404 for an unknown offer ID."""
        self._authenticate(self.owner)
        response = self.client.patch(
            "/api/offers/999999/",
            {"title": "Unknown"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_patch_returns_documented_fields(self):
        """Return the complete updated offer representation."""
        response = self._patch_as(
            self.owner,
            {"title": "Updated Offer"},
        )
        expected_fields = {
            "id",
            "title",
            "image",
            "description",
            "details",
        }
        self.assertEqual(set(response.data), expected_fields)
