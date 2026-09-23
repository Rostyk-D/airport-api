from django.core.exceptions import ValidationError
from django.db import models

from airports.models import Route


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    min_baggage_weight = models.PositiveIntegerField(
        default=2,
        help_text="Minimum baggage weight allowed for one passenger, kg.",
    )
    max_baggage_weight = models.PositiveIntegerField(
        default=10,
        help_text="Maximum baggage weight allowed for one passenger, kg.",
    )
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    def clean(self):
        if self.min_baggage_weight > self.max_baggage_weight:
            raise ValidationError(
                {
                    "max_baggage_weight": (
                        "Maximum baggage weight cannot be less "
                        "than minimum baggage weight."
                    )
                }
            )

    def __str__(self):
        return self.name


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    crew = models.ManyToManyField(
        Crew,
        related_name="flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} - {self.departure_time}"
