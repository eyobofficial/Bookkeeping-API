from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from allauth.account.adapter import get_adapter
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken

from .fields import CustomPhoneNumberField
from .exceptions import NonUniqueEmailException, NonUniquePhoneNumberException
from .models import Profile, Setting


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Custom serializer to log users with password and either
    phone number or email.
    """
    username = serializers.CharField(help_text='Phone number or email')
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Wrong username or password.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        validated_data['user'] = user
        return validated_data


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


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Setting
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
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
    tokens = serializers.SerializerMethodField()
    profile = ProfileSerializer(read_only=True)
    settings = SettingSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email', 'password',
            'first_name', 'last_name', 'is_active',
            'tokens', 'profile', 'settings'
        )

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate_phone_number(self, value):
        """
        Validate phone number is unique.
        """
        if User.objects.filter(phone_number=value).exists():
            message = 'user with this phone number already exists.'
            raise serializers.ValidationError(message)
        return value

    def get_tokens(self, obj):
        jwt = RefreshToken.for_user(obj)
        return {
            'refresh': str(jwt),
            'access': str(jwt.access_token)
        }

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        # User Object
        user = User(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email')
        )
        user.set_password(raw_password)
        user.save()

        # User Profile
        user.profile.first_name = first_name
        user.profile.last_name = last_name
        user.profile.save()

        return user


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.ReadOnlyField()
    refresh = serializers.ReadOnlyField()


class UserResponseSerializer(UserRegistrationSerializer):
    """
    Read-only representation of the `User` model
    in a successful response.
    """
    tokens = TokenResponseSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    settings = SettingSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email',
            'first_name', 'last_name', 'is_active', 'tokens',
            'profile', 'settings'
        )



class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=120, write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        max_length=120, write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value, *args, **kwargs):
        user = self.context.get('user')
        if not user.check_password(value):
            raise serializers.ValidationError('Wrong old password.')
        return value

    def validate_new_password(self, value, *args, **kwargs):
        user = self.context.get('user')
        try:
            validate_password(value, user=user)
            return value
        except ValidationError as e:
            raise

    def save(self, *args, **kwargs):
        user = self.context.get('user')
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()


class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        UntypedToken(attrs['token'])
        return {'detail': _('Token is valid')}
