from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airports", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="route",
            constraint=models.CheckConstraint(
                condition=~models.Q(source=models.F("destination")),
                name="route_source_different_from_destination",
            ),
        ),
    ]
