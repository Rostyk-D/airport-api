from rest_framework import viewsets

from flights.models import (
    Airplane,
    AirplaneType,
    Crew,
    Flight,
)
from flights.serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    FlightSerializer,
)
from users.permissions import IsAdminOrReadOnly


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrReadOnly,)
