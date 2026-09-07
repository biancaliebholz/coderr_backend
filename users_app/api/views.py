from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users_app.api.serializers import (
    LoginSerializer,
    RegistrationSerializer,
)


User = get_user_model()


class RegistrationView(CreateAPIView):
    """Create a new customer or business account."""

    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]


class LoginView(GenericAPIView):
    """Authenticate a user and return an authentication token."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
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
