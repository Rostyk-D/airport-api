from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airports.models import Airport, Route
from flights.models import Airplane, AirplaneType, Crew, Flight
from orders.models import Order, Ticket
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

    def order_payload(self, seat=1, baggage_type=1):
        return {
            "tickets": [
                {
                    "row": 1,
                    "seat": seat,
                    "flight": self.flight.id,
                    "baggage_type": baggage_type,
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

    def test_user_cannot_access_other_users_order(self):
        own_order = Order.objects.create(user=self.user)
        other_order = Order.objects.create(user=self.other_user)

        self.client.force_authenticate(self.user)

        own_response = self.client.get(
            f"/api/orders/{own_order.id}/"
        )
        other_response = self.client.get(
            f"/api/orders/{other_order.id}/"
        )

        self.assertEqual(own_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            other_response.status_code,
            status.HTTP_404_NOT_FOUND,
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
                        "baggage_type": 1,
                    },
                    {
                        "row": 1,
                        "seat": 2,
                        "flight": self.flight.id,
                        "baggage_type": 2,
                    },
                    {
                        "row": 2,
                        "seat": 3,
                        "flight": self.flight.id,
                        "baggage_type": 3,
                    },
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(len(response.data["tickets"]), 3)
        self.assertEqual(self.flight.tickets.count(), 3)

        returned_types = {
            ticket["baggage_type"]
            for ticket in response.data["tickets"]
        }
        self.assertEqual(returned_types, {1, 2, 3})

    def test_user_cannot_update_or_delete_order(self):
        order = Order.objects.create(user=self.user)
        self.client.force_authenticate(self.user)

        patch_response = self.client.patch(
            f"/api/orders/{order.id}/",
            self.order_payload(),
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
                        "baggage_type": 3,
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tickets"]), 1)
        self.assertEqual(response.data["tickets"][0]["seat"], 3)
        self.assertEqual(response.data["tickets"][0]["baggage_type"], 3)

    def test_invalid_baggage_type_is_rejected(self):
        self.client.force_authenticate(self.user)

        for invalid_type in (0, 4, 10):
            response = self.client.post(
                "/api/orders/",
                self.order_payload(baggage_type=invalid_type),
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

    def test_ticket_endpoint_is_read_only(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/tickets/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_ticket_endpoint_requires_authentication(self):
        response = self.client.get("/api/tickets/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_users_only_see_tickets_from_their_own_orders(self):
        own_order = Order.objects.create(user=self.user)
        other_order = Order.objects.create(user=self.other_user)
        Ticket.objects.create(
            row=1,
            seat=1,
            baggage_type=1,
            flight=self.flight,
            order=own_order,
        )
        Ticket.objects.create(
            row=1,
            seat=2,
            baggage_type=2,
            flight=self.flight,
            order=other_order,
        )

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["order"], own_order.id)

        self.client.force_authenticate(self.admin)
        admin_response = self.client.get("/api/tickets/")
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data["count"], 2)
