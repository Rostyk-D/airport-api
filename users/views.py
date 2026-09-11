from rest_framework import viewsets

from users.models import User
from users.serializers import UserSerializer, UserCreationSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreationSerializer
        return UserSerializer
