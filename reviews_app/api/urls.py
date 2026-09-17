from django.urls import path

from reviews_app.api.views import (
    ReviewDetailView,
    ReviewListCreateView,
)


app_name = "reviews_app"


urlpatterns = [
    path(
        "reviews/",
        ReviewListCreateView.as_view(),
        name="review-list",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewDetailView.as_view(),
        name="review-detail",
    ),
]
