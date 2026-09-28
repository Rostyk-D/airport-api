from rest_framework import serializers

from flights.models import Airplane, AirplaneType, Crew, Flight


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        for field in ("first_name", "last_name"):
            if field in attrs:
                value = attrs[field].strip()

                if not value:
                    raise serializers.ValidationError(
                        {field: "This field cannot be empty."}
                    )

                attrs[field] = value

        return attrs


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Airplane type name cannot be empty."
            )

        return value


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
        )

    def validate(self, attrs):
        if "name" in attrs:
            attrs["name"] = attrs["name"].strip()

            if not attrs["name"]:
                raise serializers.ValidationError(
                    {"name": "Airplane name cannot be empty."}
                )

        for field in ("rows", "seats_in_row"):
            if field in attrs and attrs[field] <= 0:
                raise serializers.ValidationError(
                    {field: "Value must be greater than 0."}
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

    def validate(self, attrs):
        departure_time = attrs.get(
            "departure_time",
            getattr(self.instance, "departure_time", None),
        )
        arrival_time = attrs.get(
            "arrival_time",
            getattr(self.instance, "arrival_time", None),
        )

        if (
            departure_time
            and arrival_time
            and departure_time >= arrival_time
        ):
            raise serializers.ValidationError(
                {
                    "arrival_time": (
                        "Arrival time must be later than departure time."
                    )
                }
            )

        if "crew" in attrs and not attrs["crew"]:
            raise serializers.ValidationError(
                {"crew": "At least one crew member is required."}
            )

        return attrs
