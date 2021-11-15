from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView, CreateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

from accounts import schema as account_schema
from business.models import BusinessAccount
from shared import schema as shared_schema
from shared.sms.twilio_tokens import TwilioTokenService
from shared.models import TwilioService
from .serializers import UserRegistrationSerializer, LoginSerializer, \
    ValidEmailSerialzier, ValidPhoneNumberSerialzier, ValidPhoneNumberConfirmSerialzier,\
    PasswordChangeSerializer,TokenVerifySerializer, UserResponseSerializer, \
    UserDetailSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, \
    ProfileSerializer, SettingSerializer, UserBusinessAccountSerializer, \
    PartnerRegistrationSerializer
from .permissions import IsAccountOwner, IsAccountActive, IsProfileOwner, \
    IsSettingOwner, IsBusinessOwner
from .models import Profile, Setting


User = get_user_model()


class UserLoginAPIView(GenericAPIView):
    """
    post:
    User Login

    Authenticate existing users using phone number or email and password.
    On successful authentication, a JSON Web Token (JWT) is returned in the
    response body. The response body returns the user data with *access* and
    *refresh* JWT tokens. The access token is used to perform HTTP operations
    on restricted resource. The refersh token is used to retrieve new access
    tokens when the existing token expires.

    **Token Expirations** <br />
    - Access Token: 60 minutes
    - Refresh Token: 90 days
    """
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        responses={
            200: UserResponseSerializer(),
            401: account_schema.login_401_response,
            403: account_schema.login_403_response
        },
        operation_id='user-login',
        tags=['User Account'],
        security=[],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            serializer = UserRegistrationSerializer(user)
            token = RefreshToken.for_user(user)
            data = serializer.data
            data['tokens'] = {
                'refresh': str(token),
                'access': str(token.access_token)
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        responses={
            201: UserResponseSerializer(),
            400: account_schema.registration_400_response
        },
        operation_id='user-registration',
        tags=['User Account'],
        security=[]
    )
)
class UserRegistrationAPIView(CreateAPIView):
    """
    post:
    User Registration

    The response body returns the new user data with *access* and *refresh* JWT
    tokens. The access token is used to perform HTTP operations on restricted
    resource. The refersh token is used to retrieve new access tokens when the
    existing token expires.

    **Password Requirements**
    - Username should be at least 6 characters long.
    - Password should be at least 8 characters long.
    - Password should not be similar to the user phone number or email address.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        responses={
            201: PartnerRegistrationSerializer(),
            400: account_schema.registration_400_response
        },
        operation_id='partner-registration',
        tags=['User Account'],
        badges=[{'color': 'blue', 'label': 'Dexter'}],
        security=[]
    )
)
class PartnerRegistrationAPIView(CreateAPIView):
    """
    post:
    Partner Registration

    The response body returns the new user data with *access* and *refresh* JWT
    tokens. The access token is used to perform HTTP operations on restricted
    resource. The refersh token is used to retrieve new access tokens when the
    existing token expires.

    **Password Requirements**
    - Password should be at least 8 characters long.
    - Password should not be similar to the user phone number or email address.
    """
    queryset = User.objects.all()
    serializer_class = PartnerRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class EmailValidatorAPIView(GenericAPIView):
    """
    post:
    Email Validation

    Check if submitted email is a valid email address and not registered
    in the system.
    """
    serializer_class = ValidEmailSerialzier

    @swagger_auto_schema(
        operation_id='email-validation',
        tags=['User Account'],
        security=[],
        responses={
            200: ValidEmailSerialzier(),
            400: account_schema.email_validation_400_response,
            409: account_schema.email_validation_409_response
        }
    )
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        error = {'email': [_('Enter a valid email address.')]}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberValidatorAPIView(GenericAPIView):
    """
    post:
    Phone Number Validation

    Check if submitted phone number is a valid phone number and not registered
    in the system. The phone number should be in an `E164` format.

    *NOTE: The One-Time Password (OTP) is only valid for 10 minutes.*
    """
    serializer_class = ValidPhoneNumberSerialzier

    @swagger_auto_schema(
        operation_id='phone-number-validation',
        tags=['User Account'],
        security=[],
        responses={
            200: ValidPhoneNumberSerialzier(),
            400: account_schema.phone_validation_400_response,
            409: account_schema.phone_validation_409_response
        }
    )
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Send OTP SMS
            phone_number = str(serializer.validated_data['phone_number'])
            client = TwilioTokenService(to=str(phone_number))
            client.send_verification()
            TwilioService.objects.update_or_create(
                phone_number=phone_number,
                defaults={'service_id': client.service_id}
            )
            return Response(serializer.data)

        error = {'phoneNumber': [_('Enter a valid phone number.')]}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberConfirmAPIView(GenericAPIView):
    """
    post:
    Phone Number Confirmation

    Check if submitted phone number and OTP matches to confirm the submitted
    phone number is owned by the user. The phone number should be in an `E164` format.

    *NOTE: The One-Time Password (OTP) is only valid for 10 minutes.*
    """
    serializer_class = ValidPhoneNumberConfirmSerialzier

    @swagger_auto_schema(
        operation_id='phone-number-confirmation',
        tags=['User Account'],
        security=[],
        responses={
            200: account_schema.phone_number_confirm_200_response,
            400: account_schema.phone_validation_400_response,
            404: account_schema.otp_not_found_404_response
        }
    )
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            message = {'detail': _('Phone number successfully validated.')}
            return Response(message)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(GenericAPIView):
    """
    post:
    Change Password

    Change password for authenticated users.

    **Password Requirements**
    - Password should be at least 8 characters long.
    - Password should not be similar to the user phone number or email address.
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAccountOwner]

    @swagger_auto_schema(
        operation_id='change-password',
        tags=['User Account'],
        responses={
            200: account_schema.password_change_200_response,
            400: account_schema.password_change_400_response,
            401: shared_schema.unauthorized_401_response
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(
            context={'user': user},
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            response = {'detail': _('Password changed successfully.')}
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenVerifyView(TokenVerifyView):
    """
    post:
    Token Validation

    Verify access token is a valid JWT token and is not yet expired.
    """
    serializer_class = TokenVerifySerializer

    @swagger_auto_schema(
        operation_id='token-validation',
        responses={
            200: account_schema.token_validation_200_response,
            401: account_schema.token_validation_401_response
        },
        tags=['User Account'],
        security=[]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    post:
    Token Referesh

    Returns new access token to replace an expired token.
    """

    @swagger_auto_schema(
        operation_id='token-refresh',
        responses={
            200: account_schema.token_refresh_200_response,
            401: account_schema.token_refresh_401_response
        },
        tags=['User Account']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='user-detail',
        tags=['User Account'],
        responses={
            200: UserDetailSerializer(),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        operation_id='user-update',
        tags=['User Account'],
        responses={
            200: UserDetailSerializer(),
            400: account_schema.email_validation_400_response,
            401: shared_schema.unauthorized_401_response,
            409: account_schema.email_validation_409_response,
        }
    )
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        operation_id='partial-user-update',
        tags=['User Account'],
        responses={
            200: UserDetailSerializer(),
            400: account_schema.email_validation_400_response,
            401: shared_schema.unauthorized_401_response,
            409: account_schema.email_validation_409_response
        }
    )
)
class UserDetailAPIView(RetrieveUpdateAPIView):
    """
    get:
    User Detail

    Returns the user details for an authenticated account.

    put:
    User Update

    Updates the user details for an authenticated account.

    patch:
    Partial User Update

    Partially updates the user details for an authenticated account.
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    permission_classes = [IsAccountOwner, IsAccountActive]

    def get_object(self, *args, **kwargs):
        return self.request.user


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='user-profile-detail',
        tags=['User Profile'],
        responses={
            200: ProfileSerializer(),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        operation_id='user-profile-update',
        tags=['User Profile'],
        request_body=account_schema.profile_edit_request_body,
        responses={
            200: ProfileSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.photo_not_found_404_response
        }
    )
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        operation_id='partial-user-profile-update',
        tags=['User Profile'],
        request_body=account_schema.profile_edit_request_body,
        responses={
            200: ProfileSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: shared_schema.unauthorized_401_response
        }
    )
)
class UserProfileDetailAPIView(RetrieveUpdateAPIView):
    """
    get:
    User Profile Detail

    Returns the profile details of the current authenticated user.

    put:
    User Profile Update

    Updates the profile details of the currently authenticated user.

    patch:
    Partial User Profile Update

    Partially updates the profile details of the currently authenticated user.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwner]

    def get_object(self):
        return self.request.user.profile


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='user-settings',
        tags=['Settings'],
        responses={
            200: SettingSerializer(),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        operation_id='user-settings-update',
        tags=['Settings'],
        responses={
            200: SettingSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        operation_id='partial-user-settings-update',
        tags=['Settings'],
        responses={
            200: SettingSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: shared_schema.unauthorized_401_response
        }
    )
)
class UserSettingsAPIView(RetrieveUpdateAPIView):
    """
    get:
    User Settings

    Returns the settings of the current authenticated user.

    put:
    User Settings Update

    Updates the settings of the currently authenticated user.

    patch:
    Partial User Settings Update

    Partially updates the settings of the currently authenticated user.
    """
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [IsSettingOwner]

    def get_object(self):
        return self.request.user.settings


class PasswordResetAPIView(GenericAPIView):
    """
    post:
    Password Reset

    If a user account with this phone number exists, it sends an OTP (One-time Password)
    code to the user mobile phone via SMS.

    *NOTE: The One-Time Password (OTP) is only valid for 10 minutes.*
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]


    @swagger_auto_schema(
        operation_id='password-reset',
        tags=['User Account'],
        security=[],
        responses={
            200: PasswordResetSerializer(),
            400: account_schema.password_reset_400_response,
            404: account_schema.password_reset_404_response
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Send OTP SMS
            phone_number = str(serializer.validated_data['phone_number'])
            client = TwilioTokenService(to=str(phone_number))
            client.send_verification()
            TwilioService.objects.update_or_create(
                phone_number=phone_number,
                defaults={'service_id': client.service_id}
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(GenericAPIView):
    """
    post:
    Password Reset Confirm

    Resets a forgotten password using the one-time passowrds (OTP) which
    the user received via SMS.

    **Password Requirements**
    - Password should be at least 8 characters long.
    - Password should not be similar to the user phone number or email address.

    *NOTE: The One-Time Password (OTP) is only valid for 10 minutes.*
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id='password-reset-confirm',
        responses={
            200: account_schema.password_reset_confirm_200_response,
            400: account_schema.password_reset_confirm_400_response,
            404: account_schema.password_reset_confirm_404_response
        },
        tags=['User Account'],
        security=[]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            new_password = serializer.validated_data['new_password']
            user = User.objects.get(phone_number=phone_number)
            user.set_password(new_password)
            user.save()
            message = {'detail': _('New password is set successfully.')}
            return Response(message)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: UserBusinessAccountSerializer(many=True),
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: UserBusinessAccountSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            201: UserBusinessAccountSerializer(),
            400: account_schema.user_business_account_create_400_response,
            401: shared_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='update',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: UserBusinessAccountSerializer(),
            400: account_schema.user_business_account_create_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            200: UserBusinessAccountSerializer(),
            400: account_schema.user_business_account_create_400_response,
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        tags=['Business Account'],
        responses={
            204: 'No Content',
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        }
    )
)
class BusinessAccountViewSet(ModelViewSet):
    """
    list:
    User Business Account List

    Returns a list of all business accounts for the current authenticated
    user.

    retrieve:
    User Business Account Detail

    Returns the details of a business account of the current authenticated user.

    create:
    User Business Account Create

    Creates a new business account that is tied with the current authenticated
    user.

    update:
    User Business Account Update

    Update the details of a business account of the current authenticted user.

    partial_update:
    User Business Account Partial Update

    Partially update the details of a business account of the current authenticted
    user.

    destroy:
    User Business Account Delete

    Delete a business account of the current authenticated user.
    """
    queryset = BusinessAccount.objects.all()
    serializer_class = UserBusinessAccountSerializer
    permission_classes = [IsBusinessOwner]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
