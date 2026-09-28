from rest_framework import permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import (
    EmailTokenObtainPairSerializer,
    UserCreationSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]

        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreationSerializer
        return UserSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
