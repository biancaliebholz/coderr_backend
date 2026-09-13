from rest_framework.routers import SimpleRouter

from offers_app.api.views import OfferViewSet


app_name = "offers_app"

router = SimpleRouter()
router.register(
    "offers",
    OfferViewSet,
    basename="offer",
)

urlpatterns = router.urls
