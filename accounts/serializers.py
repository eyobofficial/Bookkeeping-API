from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from twilio.base.exceptions import TwilioRestException

from business.models import BusinessAccount
from shared.fields import PhotoUploadField
from shared.models import PhotoUpload, TwilioService
from shared.sms.twilio_tokens import TwilioTokenService

from .fields import CustomPhoneNumberField
from .exceptions import NonUniqueEmailException, NonUniquePhoneNumberException,\
    AccountNotRegisteredException, WrongOTPException, \
    InvalidCredentialsException, AccountDisabledException
from .models import Profile, Setting
from .validators import is_digit


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text='Phone number or email')
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

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
    email = serializers.EmailField()

    def validate_email(self, value):
        queryset = User.objects.filter(email=value)
        if value and queryset.exists():
            raise NonUniqueEmailException()
        return value


class ValidPhoneNumberSerialzier(serializers.Serializer):
    phone_number = CustomPhoneNumberField()

    def validate_phone_number(self, value):
        queryset = User.objects.filter(phone_number=value)
        if queryset.exists():
            raise NonUniquePhoneNumberException()
        return value


class ValidPhoneNumberConfirmSerialzier(serializers.Serializer):
    phone_number = CustomPhoneNumberField()
    otp = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        queryset = User.objects.filter(phone_number=value)
        if queryset.exists():
            raise NonUniquePhoneNumberException()
        return value

    def validate(self, validated_data):
        phone_number = str(validated_data['phone_number'])
        otp = validated_data['otp']

        try:
            twilio_service = TwilioService.objects.get(phone_number=phone_number)
            client = TwilioTokenService(to=phone_number, service_id=twilio_service.service_id)
            if client.check_verification(code=otp):
                return validated_data
            raise WrongOTPException()
        except (TwilioRestException, TwilioService.DoesNotExist) as e:
            raise WrongOTPException()


class ProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    profile_photo = PhotoUploadField(required=False)

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'date_of_birth', 'address', 'city', 'country',
                  'postal_code', 'profile_photo', 'updated_at')
        ref_name = 'Profile'

    def update(self, instance, validated_data):
        photo_data = validated_data.pop('profile_photo')
        instance.profile_photo = self._get_photo(instance, photo_data)
        return super().update(instance, validated_data)

    def _get_photo(self, instance, photo_data):
        """
        Save profile photo from unploaded photo instance.

        params:
          instance(object): The user profile instance.
          photo_data(dict): The serialized dictonary of the PhotoUploaded
          instance.
        """
        photo_id = photo_data['id']
        return PhotoUpload.objects.get(pk=photo_id)


class SettingSerializer(serializers.ModelSerializer):
    font_size = serializers.IntegerField(min_value=1, max_value=50, default=11)
    terms_and_condition = serializers.NullBooleanField(default=None)

    class Meta:
        model = Setting
        fields = ('font_size', 'terms_and_condition', 'updated_at')
        ref_name = 'Settings'


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.ReadOnlyField()
    refresh = serializers.ReadOnlyField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True, required=False)
    last_name = serializers.CharField(max_length=100, write_only=True, required=False)
    pin = serializers.CharField(write_only=True,
                                min_length=4, max_length=4,
                                validators=[is_digit],
                                style={'input_type': 'password'})
    phone_number = CustomPhoneNumberField(required=True,
                                          error_messages={
                                              'invalid': _('Enter a valid phone number.')})
    is_active = serializers.BooleanField(read_only=True)
    tokens = serializers.SerializerMethodField()
    profile = ProfileSerializer(read_only=True)
    settings = SettingSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'pin', 'first_name', 'last_name', 'is_active',
                  'tokens', 'profile', 'settings')
        extra_kwargs = {
            'email': {'allow_blank': True},
            'phone_number': {'required': True}
        }

    def validate_email(self, value):
        if value and value.strip() == '':
            return None
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            err_message = _('user with this phone number already exists.')
            raise serializers.ValidationError(err_message)
        return value

    def get_tokens(self, obj):
        jwt = RefreshToken.for_user(obj)
        return {'refresh': str(jwt), 'access': str(jwt.access_token)}

    def create(self, validated_data):
        # Required fields
        phone_number = validated_data['phone_number']
        raw_pin = validated_data['pin']

        # Optional fields
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')

        # User Object
        user = User(phone_number=phone_number, email=email)
        user.pin = make_password(raw_pin)
        user.save()

        # User Profile
        if first_name and last_name:
            user.profile.first_name = first_name
            user.profile.last_name = last_name
            user.profile.save()
        return user


class PartnerRegistrationSerializer(serializers.ModelSerializer):
    tokens = TokenResponseSerializer()
    password = serializers.CharField(max_length=120,
                                     write_only=True,
                                     style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'tokens')
        extra_kwargs = {
            'username': {'required': True, 'min_length': 6},
            'email': {'required': True}
        }

    def create(self, validated_data):
        validated_data['type'] = User.PARTNER
        return super().create(validated_data)

    def get_tokens(self, obj):
        jwt = RefreshToken.for_user(obj)
        return {
            'refresh': str(jwt),
            'access': str(jwt.access_token)
        }


class UserResponseSerializer(UserRegistrationSerializer):
    tokens = TokenResponseSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    settings = SettingSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'is_active', 'tokens', 'profile', 'settings')


class UserDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    profile = ProfileSerializer(read_only=True,
                                help_text=_('A read-only representation of the user profile.'))
    settings = SettingSerializer(read_only=True,
                                 help_text=_('A read-only representation of the user profile.'))

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'is_active', 'profile', 'settings')
        read_only_fields = ('phone_number', )

    def validate_email(self, value):
        queryset = User.objects.filter(email=value)
        if value and queryset.exists():
            raise NonUniqueEmailException()
        return value


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=120, write_only=True,
                                             style={'input_type': 'password'})
    new_password = serializers.CharField(max_length=120, write_only=True,
                                         style={'input_type': 'password'})

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


class PinChangeSerializer(serializers.Serializer):
    current_pin = serializers.CharField(max_length=4,
                                        write_only=True,
                                        style={'input_type': 'password'})
    new_pin = serializers.CharField(max_length=4,
                                    write_only=True,
                                    style={'input_type': 'password'})

    def validate_current_pin(self, value, *args, **kwargs):
        user = self.context.get('user')
        if not user.check_password(value):
            err_message = _('Wrong current PIN.')
            raise serializers.ValidationError(err_message)
        return value

    def validate_new_pin(self, value, *args, **kwargs):
        if not value.isdigit():
            raise ValidationError(_('PIN must be a digit.'))
        return value

    def save(self, *args, **kwargs):
        user = self.context.get('user')
        new_pin = self.validated_data['new_pin']
        user.set_pin(new_pin)
        user.save()


class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        UntypedToken(attrs['token'])
        return {'detail': _('Token is valid')}


class PasswordResetSerializer(serializers.Serializer):
    phone_number = CustomPhoneNumberField()

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise AccountNotRegisteredException()
        return value


class PinResetSerializer(serializers.Serializer):
    phone_number = CustomPhoneNumberField()

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise AccountNotRegisteredException()
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone_number = CustomPhoneNumberField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=100)

    def validate_new_password(self, value, *args, **kwargs):
        try:
            validate_password(value)
            return value
        except ValidationError as e:
            raise

    def validate(self, validated_data):
        phone_number = str(validated_data['phone_number'])
        otp = validated_data['otp']

        try:
            twilio_service = TwilioService.objects.get(phone_number=phone_number)
            client = TwilioTokenService(to=phone_number, service_id=twilio_service.service_id)
            if client.check_verification(code=otp):
                return validated_data
            raise WrongOTPException()
        except (TwilioRestException, TwilioService.DoesNotExist) as e:
            raise WrongOTPException()


class PinResetConfirmSerializer(serializers.Serializer):
    phone_number = CustomPhoneNumberField()
    otp = serializers.CharField(max_length=6)
    new_pin = serializers.CharField(max_length=4, min_length=4)

    def validate_new_pin(self, value, *args, **kwargs):
        if not value.isdigit():
            raise ValidationError(_('PIN must be a digit.'))
        return value

    def validate(self, validated_data):
        phone_number = str(validated_data['phone_number'])
        otp = validated_data['otp']

        try:
            twilio_service = TwilioService.objects.get(phone_number=phone_number)
            client = TwilioTokenService(to=phone_number,
                                        service_id=twilio_service.service_id)
            if client.check_verification(code=otp):
                return validated_data
            raise WrongOTPException()
        except (TwilioRestException, TwilioService.DoesNotExist) as e:
            raise WrongOTPException()


class UserBusinessAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAccount
        fields = ('id', 'name', 'business_type', 'currency', 'address', 'city',
                  'country', 'postal_code', 'email', 'created_at', 'updated_at')
        extra_kwargs = {
            # Cannot be on the model since we already have null city at this point.
            'city': {'required': True},
            'country': {'default': 'NG'}
        }
