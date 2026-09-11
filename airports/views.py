from rest_framework import viewsets

from airports.models import Airport, Route
from airports.serializers import (
    AirportsSerializer,
    RouteSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportsSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
