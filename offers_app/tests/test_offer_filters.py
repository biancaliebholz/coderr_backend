"""Tests for filtering, searching, and ordering offers."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from users_app.models import Profile


User = get_user_model()


class OfferFilterTests(APITestCase):
    """Test the documented query parameters of the offer list."""

    def setUp(self):
        """Create offers with different owners, prices, and delivery times."""
        self.url = "/api/offers/"
        self.creator_one = self._create_business_user("designer")
        self.creator_two = self._create_business_user("developer")
        self.first, self.second, self.third = self._create_offers()

    def _create_business_user(self, username):
        """Create a business user for an offer."""
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

    def _create_offers(self):
        """Create three distinguishable offers."""
        first = self._create_offer(
            self.creator_one, "Logo Design", "Branding package.", 100, 5
        )
        second = self._create_offer(
            self.creator_two, "Website", "Modern application.", 300, 10
        )
        third = self._create_offer(
            self.creator_one, "SEO", "Search engine service.", 200, 3
        )
        return first, second, third

    def _create_offer(self, user, title, description, price, delivery):
        """Create an offer with three details."""
        offer = Offer.objects.create(
            user=user,
            title=title,
            description=description,
        )
        for index, offer_type in enumerate(OfferDetail.OfferType.values):
            detail_price = price + index * 100
            detail_delivery = delivery + index
            self._create_detail(
                offer, offer_type, detail_price, detail_delivery
            )
        return offer

    def _create_detail(self, offer, offer_type, price, delivery):
        """Create one detail for an offer."""
        OfferDetail.objects.create(
            offer=offer,
            title=f"{offer_type.title()} Package",
            revisions=2,
            delivery_time_in_days=delivery,
            price=price,
            features=["Feature"],
            offer_type=offer_type,
        )

    def _result_ids(self, parameters):
        """Return offer IDs for the supplied query parameters."""
        response = self.client.get(self.url, parameters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [result["id"] for result in response.data["results"]]

    def test_filter_by_creator_id(self):
        """Return only offers belonging to the requested creator."""
        result_ids = self._result_ids(
            {"creator_id": self.creator_one.id}
        )
        self.assertEqual(
            set(result_ids),
            {self.first.id, self.third.id},
        )

    def test_filter_by_minimum_price(self):
        """Return offers whose minimum price reaches the given value."""
        result_ids = self._result_ids({"min_price": 200})
        self.assertEqual(
            set(result_ids),
            {self.second.id, self.third.id},
        )

    def test_filter_by_maximum_delivery_time(self):
        """Return offers available within the given delivery time."""
        result_ids = self._result_ids({"max_delivery_time": 5})
        self.assertEqual(
            set(result_ids),
            {self.first.id, self.third.id},
        )

    def test_search_title(self):
        """Search offers through their titles."""
        result_ids = self._result_ids({"search": "website"})
        self.assertEqual(result_ids, [self.second.id])

    def test_search_description(self):
        """Search offers through their descriptions."""
        result_ids = self._result_ids({"search": "branding"})
        self.assertEqual(result_ids, [self.first.id])

    def test_order_by_minimum_price(self):
        """Order offers by their calculated minimum price."""
        result_ids = self._result_ids({"ordering": "min_price"})
        self.assertEqual(
            result_ids,
            [self.first.id, self.third.id, self.second.id],
        )

    def test_order_by_updated_at(self):
        """Order offers by their update timestamp."""
        result_ids = self._result_ids({"ordering": "updated_at"})
        self.assertEqual(
            result_ids,
            [self.first.id, self.second.id, self.third.id],
        )

    def test_custom_page_size(self):
        """Limit the number of results on a page."""
        response = self.client.get(self.url, {"page_size": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 1)

    def test_invalid_numeric_filter_returns_bad_request(self):
        """Reject an invalid numeric filter value."""
        response = self.client.get(self.url, {"min_price": "invalid"})
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
