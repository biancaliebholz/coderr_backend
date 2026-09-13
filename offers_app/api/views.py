"""Views for the offer API endpoints."""

from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from offers_app.api.filters import OfferFilter
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import (
    IsBusinessUser,
    IsOfferOwner,
)
from offers_app.api.serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferUpdateSerializer,
)
from offers_app.models import Offer, OfferDetail


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
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "options",
    ]

    def get_serializer_class(self):
        """Select the serializer matching the current API action."""
        if self.action == "list":
            return OfferListSerializer
        if self.action == "retrieve":
            return OfferRetrieveSerializer
        if self.action == "partial_update":
            return OfferUpdateSerializer
        return OfferCreateSerializer

    def get_permissions(self):
        """Return permissions matching the current API action."""
        if self.action == "list":
            classes = [AllowAny]
        elif self.action == "create":
            classes = [IsAuthenticated, IsBusinessUser]
        elif self.action in {"partial_update", "destroy"}:
            classes = [IsAuthenticated, IsOfferOwner]
        else:
            classes = self.permission_classes
        return [permission() for permission in classes]

    def perform_create(self, serializer):
        """Use the authenticated user as the offer owner."""
        serializer.save(user=self.request.user)


class OfferDetailView(RetrieveAPIView):
    """Return one offer package to authenticated users."""

    queryset = OfferDetail.objects.select_related("offer")
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]
