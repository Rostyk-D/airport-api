from rest_framework import serializers

from flights.models import Flight, Airplane, AirplaneType, Crew


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "min_baggage_weight",
            "max_baggage_weight",
            "airplane_type",
        )

    def validate(self, attrs):
        min_weight = attrs.get(
            "min_baggage_weight",
            getattr(self.instance, "min_baggage_weight", 2),
        )
        max_weight = attrs.get(
            "max_baggage_weight",
            getattr(self.instance, "max_baggage_weight", 10),
        )

        if min_weight > max_weight:
            raise serializers.ValidationError(
                {
                    "max_baggage_weight": (
                        "Maximum baggage weight cannot be less "
                        "than minimum baggage weight."
                    )
                }
            )

        return attrs


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
        )
