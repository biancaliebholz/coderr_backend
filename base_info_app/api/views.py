from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from base_info_app.api.serializers import BaseInfoSerializer
from offers_app.models import Offer
from reviews_app.models import Review
from users_app.models import Profile


class BaseInfoView(APIView):
    """Return public aggregate platform statistics."""

    permission_classes = [AllowAny]
    serializer_class = BaseInfoSerializer

    def get(self, request):
        """Return the documented platform information."""
        data = {
            "review_count": Review.objects.count(),
            "average_rating": self._average_rating(),
            "business_profile_count": Profile.objects.filter(
                type=Profile.UserType.BUSINESS,
            ).count(),
            "offer_count": Offer.objects.count(),
        }
        serializer = self.serializer_class(instance=data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _average_rating():
        """Return the average rating rounded to one decimal."""
        average = Review.objects.aggregate(
            value=Avg("rating"),
        )["value"]
        return round(average or 0, 1)
