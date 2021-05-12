from django.contrib.auth import get_user_model

from rest_framework import serializers

from accounts.serializers import UserRegistrationSerializer


User = get_user_model()


class TokenSerializer(serializers.Serializer):
    access = serializers.ReadOnlyField()
    refresh = serializers.ReadOnlyField()


class UserResponseSerializer(UserRegistrationSerializer):
    """
    Read-only representation of the `User` model
    in a successful response.
    """
    tokens = TokenSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'is_active', 'tokens')
