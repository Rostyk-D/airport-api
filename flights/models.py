from django.core.validators import MinValueValidator
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
    rows = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    seats_in_row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rows__gt=0),
                name="airplane_rows_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(seats_in_row__gt=0),
                name="airplane_seats_in_row_positive",
            ),
        ]

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

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    departure_time__lt=models.F("arrival_time"),
                ),
                name="flight_departure_before_arrival",
            ),
        ]

    def __str__(self):
        return f"{self.route} - {self.departure_time}"
