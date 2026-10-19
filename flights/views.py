from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
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
    AvailableSeatsResponseSerializer,
    CrewSerializer,
    FlightSerializer,
)
from orders.models import Ticket
from users.permissions import IsAdminOrReadOnly


@extend_schema(tags=["Crew"])
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.order_by("pk")
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema(tags=["Airplane types"])
class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.order_by("pk")
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema(tags=["Airplanes"])
class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.order_by("pk")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema(tags=["Flights"])
@extend_schema_view(
    list=extend_schema(
        summary="List and filter flights",
        description=(
            "Returns paginated flights. Filter by route, airplane, source "
            "airport, destination airport or departure date. Search supports "
            "airport names, cities, airplane names and airplane types. "
            "Use ordering to sort by departure time, arrival time or route distance."
        ),
        parameters=[
            OpenApiParameter(
                name="route",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by route ID.",
            ),
            OpenApiParameter(
                name="airplane",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by airplane ID.",
            ),
            OpenApiParameter(
                name="source",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by source airport ID.",
            ),
            OpenApiParameter(
                name="destination",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by destination airport ID.",
            ),
            OpenApiParameter(
                name="departure_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by departure date (YYYY-MM-DD).",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search airport/city, airplane and airplane type names.",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Sort by departure_time, arrival_time or route__distance."
                            " Prefix with '-' for descending order.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number.",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Results per page (maximum 100).",
            ),
        ],
    ),
)
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.order_by("departure_time", "pk")
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
    ordering = ("departure_time", "pk")

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
                        "departure_date": "Use YYYY-MM-DD format.",
                    }
                ) from exc

            queryset = queryset.filter(
                departure_time__date=parsed_date,
            )

        return queryset

    @extend_schema(
        summary="Get available seats for a flight",
        description=(
            "Returns total, occupied and available seat counts, plus every "
            "available seat identified by row and seat number."
        ),
        responses=AvailableSeatsResponseSerializer,
    )
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
