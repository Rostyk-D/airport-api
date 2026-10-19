from rest_framework import serializers

from airports.models import Airport, Route


class AirportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Airport name cannot be empty."
            )

        return value

    def validate_closest_big_city(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Closest big city cannot be empty."
            )

        return value


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )

    def validate(self, attrs):
        source = attrs.get(
            "source",
            getattr(self.instance, "source", None),
        )
        destination = attrs.get(
            "destination",
            getattr(self.instance, "destination", None),
        )

        if source and destination and source == destination:
            raise serializers.ValidationError(
                {
                    "destination": (
                        "Source and destination airports must be different."
                    )
                }
            )

        if "distance" in attrs and attrs["distance"] <= 0:
            raise serializers.ValidationError(
                {"distance": "Distance must be greater than 0."}
            )

        return attrs
