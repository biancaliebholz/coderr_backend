from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users_app.api.permissions import IsProfileOwnerOrReadOnly
from users_app.api.serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)
from users_app.models import Profile


User = get_user_model()


class RegistrationView(CreateAPIView):
    """Create a user account together with a profile and token."""

    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post", "options"]


class LoginView(GenericAPIView):
    """Authenticate a user and return their authentication data."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post", "options"]

    def post(self, request):
        """Return user information and a reusable authentication token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }
        return Response(data, status=status.HTTP_200_OK)


class ProfileDetailView(RetrieveUpdateAPIView):
    """Retrieve a profile and allow its owner to update it."""

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwnerOrReadOnly,
    ]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "head", "options"]
