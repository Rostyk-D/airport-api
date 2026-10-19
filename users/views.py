from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import (
    EmailTokenObtainPairSerializer,
    UserCreationSerializer,
    UserSerializer,
)


@extend_schema(
    tags=["Users"],
    description=(
        "Public registration is available. User listing and management require staff access."
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("pk")

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]

        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreationSerializer
        return UserSerializer


@extend_schema(
    tags=["Authentication"],
    summary="Obtain JWT tokens",
    description=(
        "Sign in using email and password. Use the access token with the "
        "Authorization: Bearer header for protected endpoints."
    ),
)
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
