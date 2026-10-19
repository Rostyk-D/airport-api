from django.core.validators import MinValueValidator
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to",
    )
    distance = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(source=models.F("destination")),
                name="route_source_different_from_destination",
            ),
        ]

    def __str__(self):
        return f"{self.source} - {self.destination}"
