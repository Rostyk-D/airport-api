from django.db import migrations, models
from django.core.validators import MaxValueValidator, MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0003_remove_baggage_weight_limits"),
        ("orders", "0003_add_baggage_weight_to_ticket"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="ticket_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Light"),
                    (2, "Medium"),
                    (3, "Heavy"),
                ],
                default=1,
                validators=[
                    MinValueValidator(1),
                    MaxValueValidator(3),
                ],
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="ticket",
            name="baggage_weight",
            field=models.PositiveSmallIntegerField(
                validators=[
                    MinValueValidator(1),
                    MaxValueValidator(10),
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("flight", "row", "seat"),
                name="unique_ticket_seat_per_flight",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    baggage_weight__gte=1,
                    baggage_weight__lte=10,
                ),
                name="ticket_baggage_weight_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ticket_type__gte=1,
                    ticket_type__lte=3,
                ),
                name="ticket_type_valid",
            ),
        ),
    ]
