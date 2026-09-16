"""URL routes for the orders API."""

from django.urls import path

from orders_app.api.views import OrderCreateView


app_name = "orders_app"


urlpatterns = [
    path(
        "orders/",
        OrderCreateView.as_view(),
        name="order-create",
    ),
]
