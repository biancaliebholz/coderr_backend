from django.contrib import admin

from offers_app.models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Configure offers in the Django admin."""

    list_display = [
        "id",
        "title",
        "user",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "title",
        "user__username",
    ]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Configure offer details in the Django admin."""

    list_display = [
        "id",
        "title",
        "offer",
        "offer_type",
        "price",
        "delivery_time_in_days",
    ]
    list_filter = ["offer_type"]
    search_fields = [
        "title",
        "offer__title",
    ]
