from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0003_remove_baggage_weight_limits"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airplane",
            name="rows",
            field=models.PositiveIntegerField(
                validators=[MinValueValidator(1)],
            ),
        ),
        migrations.AlterField(
            model_name="airplane",
            name="seats_in_row",
            field=models.PositiveIntegerField(
                validators=[MinValueValidator(1)],
            ),
        ),
        migrations.AddConstraint(
            model_name="airplane",
            constraint=models.CheckConstraint(
                condition=models.Q(rows__gt=0),
                name="airplane_rows_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="airplane",
            constraint=models.CheckConstraint(
                condition=models.Q(seats_in_row__gt=0),
                name="airplane_seats_in_row_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="flight",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    departure_time__lt=models.F("arrival_time"),
                ),
                name="flight_departure_before_arrival",
            ),
        ),
    ]
