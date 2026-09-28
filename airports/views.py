from rest_framework import viewsets

from airports.models import Airport, Route
from airports.serializers import (
    AirportsSerializer,
    RouteSerializer,
)
from users.permissions import IsAdminOrReadOnly


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportsSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrReadOnly,)
