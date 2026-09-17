"""Views for review API endpoints."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from reviews_app.api.filters import ReviewFilter
from reviews_app.api.permissions import (
    IsCustomerForReviewCreation,
    IsReviewOwner,
)
from reviews_app.api.serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
)
from reviews_app.models import Review


class ReviewListCreateView(ListCreateAPIView):
    """List reviews and allow customers to create them."""

    queryset = Review.objects.select_related(
        "reviewer",
        "business_user",
    )
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticated,
        IsCustomerForReviewCreation,
    ]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_class = ReviewFilter
    ordering_fields = [
        "updated_at",
        "rating",
    ]

    def get_serializer_class(self):
        """Select the serializer required by the HTTP method."""
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """Use the authenticated customer as reviewer."""
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """Update or delete a review owned by the user."""

    queryset = Review.objects.select_related(
        "reviewer",
        "business_user",
    )
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticated,
        IsReviewOwner,
    ]
    http_method_names = [
        "patch",
        "delete",
        "options",
    ]
