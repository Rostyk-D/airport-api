from datetime import date

from django.db.models import Q
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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
from orders.models import Ticket
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
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = (
        "route__source__name",
        "route__source__closest_big_city",
        "route__destination__name",
        "route__destination__closest_big_city",
        "airplane__name",
        "airplane__airplane_type__name",
    )
    ordering_fields = (
        "departure_time",
        "arrival_time",
        "route__distance",
    )
    ordering = ("departure_time",)

    @staticmethod
    def _positive_int_param(request, name):
        value = request.query_params.get(name)

        if value is None:
            return None

        try:
            value = int(value)
        except ValueError as exc:
            raise ValidationError(
                {name: "Must be a positive integer."}
            ) from exc

        if value <= 0:
            raise ValidationError(
                {name: "Must be a positive integer."}
            )

        return value

    def get_queryset(self):
        queryset = (
            self.queryset
            .select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type",
            )
            .prefetch_related("crew")
        )

        for param, field in (
            ("route", "route_id"),
            ("airplane", "airplane_id"),
            ("source", "route__source_id"),
            ("destination", "route__destination_id"),
        ):
            value = self._positive_int_param(self.request, param)

            if value is not None:
                queryset = queryset.filter(**{field: value})

        departure_date = self.request.query_params.get("departure_date")

        if departure_date:
            try:
                parsed_date = date.fromisoformat(departure_date)
            except ValueError as exc:
                raise ValidationError(
                    {
                        "departure_date": (
                            "Use YYYY-MM-DD format."
                        )
                    }
                ) from exc

            queryset = queryset.filter(
                departure_time__date=parsed_date,
            )

        return queryset

    @action(
        detail=True,
        methods=("get",),
        url_path="available-seats",
    )
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        airplane = flight.airplane

        booked_seats = set(
            Ticket.objects.filter(flight=flight).values_list(
                "row",
                "seat",
            )
        )

        available = [
            {"row": row, "seat": seat}
            for row in range(1, airplane.rows + 1)
            for seat in range(1, airplane.seats_in_row + 1)
            if (row, seat) not in booked_seats
        ]

        return Response(
            {
                "flight": flight.id,
                "total_seats": airplane.rows * airplane.seats_in_row,
                "occupied_seats": len(booked_seats),
                "available_seats": len(available),
                "seats": available,
            }
        )
