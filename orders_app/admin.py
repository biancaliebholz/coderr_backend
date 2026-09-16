"""Django admin configuration for orders."""

from django.contrib import admin

from orders_app.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Configure orders for the Django admin interface."""

    list_display = [
        "id",
        "title",
        "customer_user",
        "business_user",
        "status",
        "created_at",
    ]
    list_filter = [
        "status",
        "offer_type",
    ]
    search_fields = [
        "title",
        "customer_user__username",
        "business_user__username",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
