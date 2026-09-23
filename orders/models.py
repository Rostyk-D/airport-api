from django.conf import settings
from django.db import models

from flights.models import Flight


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"Order #{self.id}"


class Ticket(models.Model):
    BAGGAGE_WEIGHT_CHOICES = (
        (2, "Up to 2 kg"),
        (5, "Up to 5 kg"),
        (10, "Up to 10 kg"),
    )

    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    baggage_weight = models.PositiveSmallIntegerField(
        choices=BAGGAGE_WEIGHT_CHOICES,
        default=2,
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    def __str__(self):
        return (
            f"Flight {self.flight_id}: "
            f"row {self.row}, seat {self.seat}, "
            f"baggage {self.baggage_weight} kg"
        )
