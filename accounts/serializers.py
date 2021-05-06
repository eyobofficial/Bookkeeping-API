from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from allauth.account.adapter import get_adapter
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .fields import CustomPhoneNumberField
from .exceptions import NonUniqueEmailException, NonUniquePhoneNumberException


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, help_text='Phone number or email', )
    password = serializers.CharField(
        max_length=120,
        write_only=True,
        style={'input_type': 'password'}
    )


class ValidEmailSerialzier(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        queryset = User.objects.filter(email=value)
        if queryset.exists():
            raise NonUniqueEmailException()
        return value


class ValidPhoneNumberSerialzier(serializers.Serializer):
    phone_number = CustomPhoneNumberField()
    otp = serializers.SerializerMethodField()

    def validate_phone_number(self, value):
        queryset = User.objects.filter(phone_number=value)
        if queryset.exists():
            raise NonUniquePhoneNumberException()
        return value

    def get_otp(self, obj):
        """
        Returns an 6-digit OTP (One-Time Password) code.
        """
        return randint(100000, 999999)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=120,
        write_only=True,
        style={'input_type': 'password'}
    )
    phone_number = CustomPhoneNumberField(
        required=True,
        error_messages={
            'invalid': 'Enter a valid phone number.'
        }
    )
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email',
            'password', 'first_name', 'last_name', 'is_active'
        )

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def create(self, validated_data):
        raw_password = validated_data['password']
        user = User(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        user.set_password(raw_password)
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    access = serializers.ReadOnlyField()
    refresh = serializers.ReadOnlyField()


class UserResponseSerializer(UserSerializer):
    """
    Read-only representation of the `User` model
    in a successful response.
    """
    tokens = TokenSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email',
            'first_name', 'last_name', 'is_active', 'tokens'
        )
