from rest_framework.serializers import ModelSerializer, CharField
from rest_framework.validators import ValidationError
from .models import User


class UserSerializer(ModelSerializer):

    password = CharField(write_only=True)

    def validate(self, attrs):

        email_exists = User.objects.filter(email=attrs["email"]).exists()

        if email_exists:
            raise ValidationError("Cette adresse email est déjà utilisé !")

        return super().validate(attrs)

    def create(self, validated_data):

        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        user.save()

        return user

    class Meta:
        model = User
        # Tuple of serialized model fields (see link [2])
        fields = ["id", "first_name", "last_name", "password", "email"]
