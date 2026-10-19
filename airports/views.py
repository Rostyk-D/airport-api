from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from airports.models import Airport, Route
from airports.serializers import (
    AirportsSerializer,
    RouteSerializer,
)
from users.permissions import IsAdminOrReadOnly


@extend_schema(tags=["Airports"])
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.order_by("pk")
    serializer_class = AirportsSerializer
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema(tags=["Routes"])
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.order_by("pk")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrReadOnly,)
