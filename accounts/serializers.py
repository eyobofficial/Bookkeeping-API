from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken

from shared.utils.otp import generate_otp
from .fields import CustomPhoneNumberField, TimestampField
from .exceptions import NonUniqueEmailException, NonUniquePhoneNumberException,\
    AccountNotRegisteredException, InvalidCodeException, \
    InvalidCredentialsException, AccountDisabledException
from .models import Profile, Setting, PasswordResetCode
from .sms.otp import OTPSMS


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Custom serializer to log users with phone number or email
    and password.
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
            raise InvalidCredentialsException()

        if not user.is_active:
            raise AccountDisabledException()

        validated_data['user'] = user
        return validated_data


class ValidEmailSerialzier(serializers.Serializer):
    """
    Check email address for valid email format and non-duplication.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        queryset = User.objects.filter(email=value)
        if queryset.exists():
            raise NonUniqueEmailException()
        return value


class ValidPhoneNumberSerialzier(serializers.Serializer):
    """
    Check phone number for valid phone number format and non-duplication.
    """
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
        return generate_otp()


class ProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    """
    Serializer for the user profile model.
    """

    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'address', 'city',
            'country', 'postal_code', 'profile_photo', 'updated_at'
        )
        read_only_fields = ('profile_photo', 'updated_at')
        ref_name = 'Profile'


class SettingSerializer(serializers.ModelSerializer):
    """
    Serializer for the user setting model.
    """
    font_size = serializers.IntegerField(min_value=1, max_value=50, default=11)
    terms_and_condition = serializers.NullBooleanField(default=None)

    class Meta:
        model = Setting
        fields = ('font_size', 'terms_and_condition', 'updated_at')
        ref_name = 'Settings'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registrating new users.
    """
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
            'invalid': _('Enter a valid phone number.')
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
        extra_kwargs = {
            'email': {'allow_blank': True}
        }

    def validate_email(self, value):
        """
        Convert blank values to None values.
        """
        if value.strip() == '':
            return None
        return value

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate_phone_number(self, value):
        """
        Validate phone number is unique.
        """
        if User.objects.filter(phone_number=value).exists():
            err_message = _('user with this phone number already exists.')
            raise serializers.ValidationError(err_message)
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
    """
    A read-only representation of the token response for including
    in the API documentation.
    """
    access = serializers.ReadOnlyField()
    refresh = serializers.ReadOnlyField()


class UserResponseSerializer(UserRegistrationSerializer):
    """
    Read-only representation of the `User` model in a successful response.
    """
    tokens = TokenResponseSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    settings = SettingSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email', 'is_active', 'tokens',
            'profile', 'settings'
        )


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for a User model serializer.
    """
    email = serializers.EmailField()
    profile = ProfileSerializer(
        read_only=True,
        help_text=_('A read-only representation of the user profile.')
    )
    settings = SettingSerializer(
        read_only=True,
        help_text=_('A read-only representation of the user profile.')
    )

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'is_active', 'profile', 'settings')
        read_only_fields = ('phone_number', )

    def validate_email(self, value):
        """
        Check if email is unique or raise `409 Conflict` error.
        """
        queryset = User.objects.filter(email=value)
        if queryset.exists():
            raise NonUniqueEmailException()
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    current_password = serializers.CharField(
        max_length=120, write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        max_length=120, write_only=True,
        style={'input_type': 'password'}
    )

    def validate_current_password(self, value, *args, **kwargs):
        user = self.context.get('user')
        if not user.check_password(value):
            err_message = _('Wrong current password.')
            raise serializers.ValidationError(err_message)
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
    """
    Serializer for verifying access tokens.

    This serializer is adapation of the `TokenVerifySerializer` from
    the `django-rest-simplejwt` library.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        UntypedToken(attrs['token'])
        return {'detail': _('Token is valid')}


class PasswordResetSerializer(serializers.ModelSerializer):
    phone_number = CustomPhoneNumberField()
    expire_at = TimestampField(
        read_only=True,
        help_text='Timestamp in milliseconds (JS-style).'
    )

    class Meta:
        model = PasswordResetCode
        fields = ('phone_number', 'otp', 'expire_at')
        read_only_fields = ('otp', 'expire_at')
        extra_kwargs = {
            'otp': {'help_text': 'A 6-digit numeric only one-time password.'}
        }

    def validate_phone_number(self, value):
        # Make sure account exists
        if not User.objects.filter(phone_number=value).exists():
            raise AccountNotRegisteredException()
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        now = timezone.now()
        reset_otp, _ = PasswordResetCode.objects.filter(
            expire_at__gt=now
        ).get_or_create(user=user)

        # Send OTP SMS
        # TODO: Move to a celery task
        sms = OTPSMS()
        sms.recipients = str(phone_number)
        sms.message = reset_otp.otp
        sms.send()

        return reset_otp


class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    phone_number = CustomPhoneNumberField()
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = PasswordResetCode
        fields = ('otp', 'phone_number', 'new_password')
        extra_kwargs = {
            'otp': {'required': True}
        }

    def validate_new_password(self, value, *args, **kwargs):
        try:
            validate_password(value)
            return value
        except ValidationError as e:
            raise

    def validate(self, validated_data):
        now = timezone.now()
        phone_number = validated_data['phone_number']
        otp = validated_data['otp']

        try:
            query_params = {
                'user__phone_number': phone_number,
                'otp': otp,
                'expire_at__gt': now
            }
            reset_code = PasswordResetCode.objects.get(**query_params)
            validated_data['instance'] = reset_code
            return validated_data
        except PasswordResetCode.DoesNotExist:
            raise InvalidCodeException()

    def save(self):
        instance = self.validated_data['instance']
        instance.user.set_password(self.validated_data['new_password'])
        instance.user.save()
        instance.delete()
