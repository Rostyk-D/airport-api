from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import (
    EmailTokenObtainPairSerializer,
    UserCreationSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreationSerializer
        return UserSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
