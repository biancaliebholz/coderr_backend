"""Views for the orders API."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.api.permissions import (
    IsAssignedBusinessUser,
    IsCustomer,
)
from orders_app.api.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)
from orders_app.models import Order
from users_app.models import Profile


User = get_user_model()


class OrderListCreateView(ListCreateAPIView):
    """List related orders or create an order as a customer."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "options"]

    def get_queryset(self):
        """Return orders involving the authenticated user."""
        user = self.request.user
        return self.queryset.filter(
            Q(customer_user=user)
            | Q(business_user=user)
        )

    def get_serializer_class(self):
        """Use the creation serializer only for POST requests."""
        if self.request.method == "POST":
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Require a customer profile only for order creation."""
        permissions = super().get_permissions()
        if self.request.method == "POST":
            permissions.append(IsCustomer())
        return permissions


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """Update an order status or delete an order as staff."""

    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "delete", "options"]

    def get_permissions(self):
        """Select permissions according to the requested action."""
        permissions = super().get_permissions()
        if self.request.method == "PATCH":
            permissions.append(IsAssignedBusinessUser())
        elif self.request.method == "DELETE":
            permissions.append(IsAdminUser())
        return permissions


class BaseOrderCountView(APIView):
    """Provide a configurable order count for a business user."""

    permission_classes = [IsAuthenticated]
    status_value = None
    response_key = None

    def get(self, request, business_user_id):
        """Return the configured order count."""
        business_user = self._get_business_user(business_user_id)
        count = Order.objects.filter(
            business_user=business_user,
            status=self.status_value,
        ).count()
        return Response({self.response_key: count})

    def _get_business_user(self, user_id):
        """Return a business user or raise a 404 response."""
        queryset = User.objects.select_related("profile")
        return get_object_or_404(
            queryset,
            pk=user_id,
            profile__type=Profile.UserType.BUSINESS,
        )


class OrderCountView(BaseOrderCountView):
    """Count in-progress orders for a business user."""

    status_value = Order.Status.IN_PROGRESS
    response_key = "order_count"


class CompletedOrderCountView(BaseOrderCountView):
    """Count completed orders for a business user."""

    status_value = Order.Status.COMPLETED
    response_key = "completed_order_count"
