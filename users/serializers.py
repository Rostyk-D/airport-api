from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )


class UserCreationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed(
                "Invalid email or password."
            ) from exc
        except User.MultipleObjectsReturned as exc:
            raise AuthenticationFailed(
                "Invalid email or password."
            ) from exc

        if not user.is_active or not user.check_password(password):
            raise AuthenticationFailed("Invalid email or password.")

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
