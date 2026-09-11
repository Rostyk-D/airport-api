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

class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
