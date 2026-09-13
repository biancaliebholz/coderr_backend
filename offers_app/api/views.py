from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from offers_app.api.permissions import IsBusinessUser
from offers_app.api.serializers import OfferCreateSerializer
from offers_app.models import Offer


class OfferViewSet(ModelViewSet):
    """Provide API operations for offers."""

    queryset = Offer.objects.prefetch_related("details")
    serializer_class = OfferCreateSerializer
    permission_classes = [
        IsAuthenticated,
        IsBusinessUser,
    ]
    http_method_names = ["post", "options"]

    def perform_create(self, serializer):
        """Use the authenticated user as the offer owner."""
        serializer.save(user=self.request.user)
