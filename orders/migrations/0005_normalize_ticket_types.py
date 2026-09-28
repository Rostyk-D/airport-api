from django.db import migrations, models


def set_ticket_types(apps, schema_editor):
    Ticket = apps.get_model("orders", "Ticket")

    for ticket in Ticket.objects.all().iterator():
        if ticket.baggage_weight <= 2:
            ticket.ticket_type = 1
        elif ticket.baggage_weight <= 5:
            ticket.ticket_type = 2
        else:
            ticket.ticket_type = 3

        ticket.save(update_fields=["ticket_type"])


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_add_ticket_types_and_constraints"),
    ]

    operations = [
        migrations.RunPython(
            set_ticket_types,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        ticket_type=1,
                        baggage_weight__gte=1,
                        baggage_weight__lte=2,
                    )
                    | models.Q(
                        ticket_type=2,
                        baggage_weight__gte=3,
                        baggage_weight__lte=5,
                    )
                    | models.Q(
                        ticket_type=3,
                        baggage_weight__gte=6,
                        baggage_weight__lte=10,
                    )
                ),
                name="ticket_type_baggage_range_valid",
            ),
        ),
    ]
