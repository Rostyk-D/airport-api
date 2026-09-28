from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from orders.models import Order, Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "ticket_type",
            "baggage_weight",
            "order",
        )
        read_only_fields = ("id", "order")

    def validate(self, attrs):
        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]
        ticket_type = attrs["ticket_type"]
        baggage_weight = attrs["baggage_weight"]

        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError(
                {
                    "flight": (
                        "You cannot book a ticket for a flight "
                        "that has already departed."
                    )
                }
            )

        min_weight, max_weight = (
            Ticket.TICKET_TYPE_WEIGHT_RANGES[ticket_type]
        )

        if not min_weight <= baggage_weight <= max_weight:
            raise serializers.ValidationError(
                {
                    "baggage_weight": (
                        f"Ticket type {ticket_type} allows baggage "
                        f"from {min_weight} to {max_weight} kg."
                    )
                }
            )

        airplane = flight.airplane

        if row < 1 or row > airplane.rows:
            raise serializers.ValidationError(
                {
                    "row": (
                        f"Row must be between 1 and {airplane.rows}."
                    )
                }
            )

        if seat < 1 or seat > airplane.seats_in_row:
            raise serializers.ValidationError(
                {
                    "seat": (
                        f"Seat must be between 1 and "
                        f"{airplane.seats_in_row}."
                    )
                }
            )

        occupied_seats = Ticket.objects.filter(
            flight=flight,
            row=row,
            seat=seat,
        )

        current_order = self.context.get("order_instance")
        if current_order is not None:
            occupied_seats = occupied_seats.exclude(
                order=current_order
            )

        if occupied_seats.exists():
            raise serializers.ValidationError(
                {
                    "seat": (
                        "This seat is already booked for this flight."
                    )
                }
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "user",
            "tickets",
        )
        read_only_fields = (
            "id",
            "created_at",
            "user",
        )

    def validate(self, attrs):
        tickets = attrs.get("tickets")

        if self.instance is None and not tickets:
            raise serializers.ValidationError(
                {"tickets": "An order must contain at least one ticket."}
            )

        if tickets is not None and not tickets:
            raise serializers.ValidationError(
                {"tickets": "An order must contain at least one ticket."}
            )

        seats = set()

        for ticket in tickets or []:
            seat_key = (
                ticket["flight"].id,
                ticket["row"],
                ticket["seat"],
            )

            if seat_key in seats:
                raise serializers.ValidationError(
                    {
                        "tickets": (
                            "The same seat cannot be added twice "
                            "to the same flight in one order."
                        )
                    }
                )

            seats.add(seat_key)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        try:
            order = Order.objects.create(
                user=self.context["request"].user,
            )

            for ticket_data in tickets_data:
                Ticket.objects.create(
                    order=order,
                    **ticket_data,
                )
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "tickets": (
                        "One or more selected seats are no longer "
                        "available."
                    )
                }
            ) from exc

        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        tickets_data = validated_data.pop("tickets", None)
        instance = super().update(instance, validated_data)

        if tickets_data is not None:
            try:
                Ticket.objects.filter(order=instance).delete()

                for ticket_data in tickets_data:
                    Ticket.objects.create(
                        order=instance,
                        **ticket_data,
                    )
            except IntegrityError as exc:
                raise serializers.ValidationError(
                    {
                        "tickets": (
                            "One or more selected seats are no longer "
                            "available."
                        )
                    }
                ) from exc

        return instance
