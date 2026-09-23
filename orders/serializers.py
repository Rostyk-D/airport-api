from django.db import transaction
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
            "baggage_weight",
            "order",
        )
        read_only_fields = ("id", "order")

    def validate(self, attrs):
        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]
        baggage_weight = attrs["baggage_weight"]

        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError(
                "You cannot book a ticket for a flight "
                "that has already departed."
            )

        airplane = flight.airplane

        if baggage_weight < airplane.min_baggage_weight:
            raise serializers.ValidationError(
                {
                    "baggage_weight": (
                        f"Baggage weight cannot be less than "
                        f"{airplane.min_baggage_weight} kg."
                    )
                }
            )

        if baggage_weight > airplane.max_baggage_weight:
            raise serializers.ValidationError(
                {
                    "baggage_weight": (
                        f"Baggage weight cannot be greater than "
                        f"{airplane.max_baggage_weight} kg."
                    )
                }
            )

        if row < 1 or row > airplane.rows:
            raise serializers.ValidationError(
                {
                    "row": (
                        f"Row must be between 1 and "
                        f"{airplane.rows}."
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

        if Ticket.objects.filter(
            flight=flight,
            row=row,
            seat=seat,
        ).exists():
            raise serializers.ValidationError(
                "This seat is already booked for this flight."
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

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

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        order = Order.objects.create(
            user=self.context["request"].user
        )

        for ticket_data in tickets_data:
            Ticket.objects.create(
                order=order,
                **ticket_data,
            )

        return order

    def validate(self, attrs):
        tickets = attrs.get("tickets", [])
        seats = set()

        for ticket in tickets:
            seat_key = (
                ticket["flight"].id,
                ticket["row"],
                ticket["seat"],
            )

            if seat_key in seats:
                raise serializers.ValidationError(
                    "The same seat cannot be added twice "
                    "to the same flight."
                )

            seats.add(seat_key)

        return attrs
