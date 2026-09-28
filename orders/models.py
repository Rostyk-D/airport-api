from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
    TICKET_TYPE_CHOICES = (
        (1, "Light"),
        (2, "Medium"),
        (3, "Heavy"),
    )

    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    ticket_type = models.PositiveSmallIntegerField(
        choices=TICKET_TYPE_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(3),
        ],
    )
    baggage_weight = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("flight", "row", "seat"),
                name="unique_ticket_seat_per_flight",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    baggage_weight__gte=1,
                    baggage_weight__lte=10,
                ),
                name="ticket_baggage_weight_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    ticket_type__gte=1,
                    ticket_type__lte=3,
                ),
                name="ticket_type_valid",
            ),
        ]

    def __str__(self):
        return (
            f"Flight {self.flight_id}: "
            f"row {self.row}, seat {self.seat}, "
            f"type {self.ticket_type}, "
            f"baggage {self.baggage_weight} kg"
        )
