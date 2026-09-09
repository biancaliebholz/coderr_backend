from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users_app.models import Profile, User


class ProfileInline(admin.StackedInline):
    """Display the profile inside the related user administration."""

    model = Profile
    can_delete = False
    extra = 1
    max_num = 1


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Manage Coderr users together with their profiles."""

    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Manage and search Coderr profiles."""

    list_display = [
        "user",
        "type",
        "location",
        "uploaded_at",
    ]
    list_filter = ["type"]
    search_fields = [
        "user__username",
        "user__email",
    ]
    list_select_related = ["user"]
