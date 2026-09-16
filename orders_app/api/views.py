"""Views for the orders API."""

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from orders_app.api.permissions import IsCustomer
from orders_app.api.serializers import OrderCreateSerializer
from orders_app.models import Order


class OrderCreateView(CreateAPIView):
    """Create an order from an existing offer detail."""

    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    http_method_names = ["post", "options"]
