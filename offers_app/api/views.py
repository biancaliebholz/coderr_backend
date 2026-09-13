from django.db.models import Min
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsBusinessUser
from offers_app.api.serializers import (
    OfferCreateSerializer,
    OfferListSerializer,
)
from offers_app.models import Offer


class OfferViewSet(ModelViewSet):
    """Provide API operations for offers."""

    queryset = (
        Offer.objects.select_related("user")
        .prefetch_related("details")
        .annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min(
                "details__delivery_time_in_days"
            ),
        )
        .order_by("-updated_at")
    )
    serializer_class = OfferCreateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OfferPagination
    http_method_names = ["get", "post", "options"]

    def get_serializer_class(self):
        """Select the serializer matching the current API action."""
        if self.action == "list":
            return OfferListSerializer
        return OfferCreateSerializer

    def get_permissions(self):
        """Return permissions matching the current API action."""
        if self.action == "list":
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsBusinessUser]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Use the authenticated user as the offer owner."""
        serializer.save(user=self.request.user)
