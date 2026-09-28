from rest_framework import status
from rest_framework.test import APITestCase

from airports.models import Airport, Route


class AirportAndRouteValidationTests(APITestCase):
    def test_route_cannot_use_same_airport(self):
        airport = Airport.objects.create(
            name="Lviv Airport",
            closest_big_city="Lviv",
        )

        response = self.client.post(
            "/api/routes/",
            {
                "source": airport.id,
                "destination": airport.id,
                "distance": 100,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_route_distance_must_be_positive(self):
        source = Airport.objects.create(
            name="Lviv Airport",
            closest_big_city="Lviv",
        )
        destination = Airport.objects.create(
            name="Warsaw Airport",
            closest_big_city="Warsaw",
        )

        response = self.client.post(
            "/api/routes/",
            {
                "source": source.id,
                "destination": destination.id,
                "distance": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
