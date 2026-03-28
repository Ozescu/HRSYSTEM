from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Company, Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "date_joined",
        )
        read_only_fields = ("id", "is_staff", "date_joined")


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "bio",
            "phone_number",
            "profile_picture",
            "linkedin_url",
            "github_url",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "owner",
            "name",
            "description",
            "website",
            "location",
            "logo",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(request=request, email=attrs["email"], password=attrs["password"])

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs


class JWTTokenPlaceholderSerializer(serializers.Serializer):
    """
    Placeholder serializer for future JWT integration.
    Add access/refresh token fields once SimpleJWT endpoints are introduced.
    """

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
