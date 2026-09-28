from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0002_add_baggage_weight_limits"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="airplane",
            name="airplane_baggage_weight_range_valid",
        ),
        migrations.RemoveField(
            model_name="airplane",
            name="min_baggage_weight",
        ),
        migrations.RemoveField(
            model_name="airplane",
            name="max_baggage_weight",
        ),
    ]
