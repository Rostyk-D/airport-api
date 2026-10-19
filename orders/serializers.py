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
            "baggage_type",
            "order",
        )
        read_only_fields = ("id", "order")

    def validate(self, attrs):
        # During partial updates, validate the final ticket state rather than
        # skipping validation when one of the fields is omitted.
        flight = attrs.get("flight", getattr(self.instance, "flight", None))
        row = attrs.get("row", getattr(self.instance, "row", None))
        seat = attrs.get("seat", getattr(self.instance, "seat", None))

        if flight and flight.departure_time <= timezone.now():
            raise serializers.ValidationError(
                {
                    "flight": (
                        "You cannot book a ticket for a flight "
                        "that has already departed."
                    )
                }
            )

        # A partially populated serializer may not have enough information
        # to validate a new ticket. Existing tickets use their instance values.
        if flight is None or row is None or seat is None:
            return attrs

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
            # Nested ticket fields are required by TicketSerializer, but keep
            # this validation defensive if the serializer changes later.
            flight = ticket.get("flight")
            row = ticket.get("row")
            seat = ticket.get("seat")
            if flight is None or row is None or seat is None:
                continue

            seat_key = (flight.id, row, seat)

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
