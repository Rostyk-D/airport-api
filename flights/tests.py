from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airports.models import Airport, Route
from flights.models import Airplane, AirplaneType, Crew, Flight
from orders.models import Order, Ticket
from users.models import User


class FlightApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="StrongPass123!",
            is_staff=True,
        )

        source = Airport.objects.create(
            name="Lviv Airport",
            closest_big_city="Lviv",
        )
        destination = Airport.objects.create(
            name="Warsaw Airport",
            closest_big_city="Warsaw",
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=400,
        )
        airplane_type = AirplaneType.objects.create(name="Boeing")
        airplane = Airplane.objects.create(
            name="Boeing 737",
            rows=2,
            seats_in_row=3,
            airplane_type=airplane_type,
        )
        crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )
        departure = timezone.now() + timedelta(days=2)
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=departure,
            arrival_time=departure + timedelta(hours=2),
        )
        self.flight.crew.add(crew)

    def test_regular_user_cannot_create_flight(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/flights/",
            {
                "route": self.flight.route_id,
                "airplane": self.flight.airplane_id,
                "crew": list(
                    self.flight.crew.values_list("id", flat=True)
                ),
                "departure_time": (
                    timezone.now() + timedelta(days=3)
                ).isoformat(),
                "arrival_time": (
                    timezone.now() + timedelta(days=3, hours=2)
                ).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_flight(self):
        self.client.force_authenticate(self.admin)

        departure = timezone.now() + timedelta(days=3)
        response = self.client.post(
            "/api/flights/",
            {
                "route": self.flight.route_id,
                "airplane": self.flight.airplane_id,
                "crew": list(
                    self.flight.crew.values_list("id", flat=True)
                ),
                "departure_time": departure.isoformat(),
                "arrival_time": (
                    departure + timedelta(hours=2)
                ).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_flight_requires_arrival_after_departure(self):
        self.client.force_authenticate(self.admin)
        departure = timezone.now() + timedelta(days=3)

        response = self.client.post(
            "/api/flights/",
            {
                "route": self.flight.route_id,
                "airplane": self.flight.airplane_id,
                "crew": list(
                    self.flight.crew.values_list("id", flat=True)
                ),
                "departure_time": departure.isoformat(),
                "arrival_time": (
                    departure - timedelta(hours=1)
                ).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_available_seats_returns_booked_and_free_seats(self):
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(
            row=1,
            seat=1,
            ticket_type=1,
            baggage_weight=2,
            flight=self.flight,
            order=order,
        )

        response = self.client.get(
            f"/api/flights/{self.flight.id}/available-seats/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_seats"], 6)
        self.assertEqual(response.data["occupied_seats"], 1)
        self.assertEqual(response.data["available_seats"], 5)
        self.assertNotIn(
            {"row": 1, "seat": 1},
            response.data["seats"],
        )

    def test_flight_filters_by_departure_date(self):
        response = self.client.get(
            "/api/flights/",
            {
                "departure_date": (
                    self.flight.departure_time.date().isoformat()
                )
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_flight_list_is_paginated(self):
        response = self.client.get(
            "/api/flights/",
            {"page_size": 1},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
