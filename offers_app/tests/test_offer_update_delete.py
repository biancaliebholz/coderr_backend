"""Tests for updating and deleting offers through the API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from users_app.models import Profile


User = get_user_model()


UPDATE_RESPONSE_FIELDS = {
    "id",
    "title",
    "image",
    "description",
    "details",
}


class OfferUpdateDeleteTests(APITestCase):
    """Test owner-protected update and delete operations."""

    def setUp(self):
        """Create two business users and their offers."""
        self.owner = self._create_business_user("owner")
        self.other_user = self._create_business_user("other")
        self.offer = self._create_offer(self.owner, "Design Package")
        self.basic = self._create_detail(self.offer, "basic", 100)
        self._create_detail(self.offer, "standard", 200)
        self._create_detail(self.offer, "premium", 500)
        other_offer = self._create_offer(self.other_user, "Other Offer")
        self.foreign_detail = self._create_detail(
            other_offer, "basic", 80
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
        """Create an offer owned by the supplied user."""
        return Offer.objects.create(
            user=user,
            title=title,
            description="Professional design service.",
        )

    def _create_detail(self, offer, offer_type, price):
        """Create one package belonging to an offer."""
        return OfferDetail.objects.create(
            offer=offer,
            title=f"{offer_type.title()} Design",
            revisions=2,
            delivery_time_in_days=5,
            price=price,
            features=["Logo Design"],
            offer_type=offer_type,
        )

    def _updated_detail_data(self):
        """Return valid update data for the basic package."""
        return {
            "id": self.basic.pk,
            "title": "Basic Design Updated",
            "revisions": 3,
            "delivery_time_in_days": 6,
            "price": "120.00",
            "features": ["Logo Design", "Flyer"],
            "offer_type": "basic",
        }

    def _patch_as(self, user, payload):
        """Send a PATCH request as the supplied user."""
        self.client.force_authenticate(user=user)
        return self.client.patch(self.url, payload, format="json")

    def _delete_as(self, user):
        """Send a DELETE request as the supplied user."""
        self.client.force_authenticate(user=user)
        return self.client.delete(self.url)

    def test_patch_requires_authentication(self):
        """Reject an unauthenticated update."""
        response = self.client.patch(
            self.url,
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_non_owner_cannot_update_offer(self):
        """Reject an update from a different user."""
        response = self._patch_as(
            self.other_user,
            {"title": "Updated"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_update_only_supplied_fields(self):
        """Update supplied fields and preserve omitted fields."""
        old_description = self.offer.description
        response = self._patch_as(
            self.owner,
            {"title": "Updated Design Package"},
        )
        self.offer.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.offer.title, "Updated Design Package")
        self.assertEqual(self.offer.description, old_description)

    def test_patch_returns_documented_fields(self):
        """Return the documented response after an update."""
        response = self._patch_as(
            self.owner,
            {"title": "Updated Design Package"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), UPDATE_RESPONSE_FIELDS)

    def test_owner_can_update_one_offer_detail(self):
        """Update one package without replacing its database row."""
        original_id = self.basic.pk
        payload = {"details": [self._updated_detail_data()]}
        response = self._patch_as(self.owner, payload)
        self.basic.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic.pk, original_id)
        self.assertEqual(self.basic.title, "Basic Design Updated")
        self.assertEqual(self.offer.details.count(), 3)

    def test_detail_update_requires_id(self):
        """Reject nested detail data without its existing ID."""
        detail_data = self._updated_detail_data()
        detail_data.pop("id")
        response = self._patch_as(
            self.owner,
            {"details": [detail_data]},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_detail_update_requires_offer_type(self):
        """Reject nested detail data without its package type."""
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
        """Prevent modification of a package from another offer."""
        detail_data = self._updated_detail_data()
        detail_data["id"] = self.foreign_detail.pk
        response = self._patch_as(
            self.owner,
            {"details": [detail_data]},
        )
        self.foreign_detail.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.foreign_detail.title, "Basic Design Updated")

    def test_updating_unknown_offer_returns_not_found(self):
        """Return 404 when the offer does not exist."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            "/api/offers/999999/",
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_requires_authentication(self):
        """Reject an unauthenticated deletion."""
        response = self.client.delete(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_non_owner_cannot_delete_offer(self):
        """Reject deletion by a different user."""
        response = self._delete_as(self.other_user)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_delete_offer(self):
        """Allow the owner to delete their offer."""
        response = self._delete_as(self.owner)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Offer.objects.filter(pk=self.offer.pk).exists()
        )

    def test_deleting_unknown_offer_returns_not_found(self):
        """Return 404 when the offer does not exist."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete("/api/offers/999999/")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
