from django.contrib import admin

from reviews_app.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Configure reviews in the Django admin interface."""

    list_display = [
        "id",
        "reviewer",
        "business_user",
        "rating",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "rating",
        "created_at",
    ]
    search_fields = [
        "reviewer__username",
        "business_user__username",
        "description",
    ]
    ordering = [
        "-updated_at",
    ]
