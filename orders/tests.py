from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airports.models import Airport, Route
from flights.models import Airplane, AirplaneType, Crew, Flight
from orders.models import Order
from users.models import User


class OrderAndTicketApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            username="user2",
            email="user2@example.com",
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

    def order_payload(self, seat=1, ticket_type=1, baggage_weight=2):
        return {
            "tickets": [
                {
                    "row": 1,
                    "seat": seat,
                    "flight": self.flight.id,
                    "ticket_type": ticket_type,
                    "baggage_weight": baggage_weight,
                }
            ]
        }

    def test_unauthenticated_user_cannot_access_orders(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_sees_only_own_orders(self):
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.other_user)

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["user"],
            self.user.id,
        )

    def test_admin_sees_all_orders(self):
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.other_user)

        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_user_can_create_order_with_multiple_tickets(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/orders/",
            {
                "tickets": [
                    {
                        "row": 1,
                        "seat": 1,
                        "flight": self.flight.id,
                        "ticket_type": 1,
                        "baggage_weight": 2,
                    },
                    {
                        "row": 1,
                        "seat": 2,
                        "flight": self.flight.id,
                        "ticket_type": 2,
                        "baggage_weight": 5,
                    },
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tickets"]), 2)
        self.assertEqual(
            self.flight.tickets.count(),
            2,
        )

    def test_user_cannot_update_or_delete_order(self):
        order = Order.objects.create(user=self.user)
        self.client.force_authenticate(self.user)

        patch_response = self.client.patch(
            f"/api/orders/{order.id}/",
            {"tickets": self.order_payload()["tickets"]},
            format="json",
        )
        delete_response = self.client.delete(
            f"/api/orders/{order.id}/"
        )

        self.assertEqual(
            patch_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            delete_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_replace_tickets_in_order(self):
        self.client.force_authenticate(self.user)
        order_response = self.client.post(
            "/api/orders/",
            self.order_payload(),
            format="json",
        )

        self.assertEqual(
            order_response.status_code,
            status.HTTP_201_CREATED,
        )

        order_id = order_response.data["id"]

        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/orders/{order_id}/",
            {
                "tickets": [
                    {
                        "row": 2,
                        "seat": 3,
                        "flight": self.flight.id,
                        "ticket_type": 3,
                        "baggage_weight": 10,
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tickets"]), 1)
        self.assertEqual(response.data["tickets"][0]["seat"], 3)

    def test_ticket_type_matches_baggage_range(self):
        self.client.force_authenticate(self.user)

        invalid_payloads = (
            self.order_payload(
                seat=1,
                ticket_type=1,
                baggage_weight=3,
            ),
            self.order_payload(
                seat=2,
                ticket_type=2,
                baggage_weight=2,
            ),
            self.order_payload(
                seat=3,
                ticket_type=3,
                baggage_weight=5,
            ),
        )

        for payload in invalid_payloads:
            response = self.client.post(
                "/api/orders/",
                payload,
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )

    def test_same_seat_cannot_be_booked_twice(self):
        self.client.force_authenticate(self.user)

        first = self.client.post(
            "/api/orders/",
            self.order_payload(),
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(
            "/api/orders/",
            self.order_payload(),
            format="json",
        )
        self.assertEqual(
            second.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_order_must_have_at_least_one_ticket(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/orders/",
            {"tickets": []},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
