from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "password", "role"]
        read_only_fields = [
            "id",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user_profile = UserProfile(**validated_data)
        user_profile.set_password(password)
        user_profile.save()
        return user_profile


class TokenRevokeSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, required=True)

    def create(self, validated_data):
        refresh_token = validated_data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return TokenRevokeSerializer()
