from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView, CreateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

from accounts import schema as account_schema
from .serializers import UserRegistrationSerializer, LoginSerializer, \
    ValidEmailSerialzier, ValidPhoneNumberSerialzier, PasswordChangeSerializer,\
    TokenVerifySerializer, UserResponseSerializer, UserDetailSerializer, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, ProfileSerializer,\
    SettingSerializer
from .sms.otp import OTPSMS
from .permissions import IsAccountOwner, IsAccountActive, IsProfileOwner, \
    IsSettingOwner
from .models import Profile, Setting, PasswordResetCode


User = get_user_model()


class UserLoginAPIView(GenericAPIView):
    """
    post:
    User Login

    Authenticate existing users using phone number or email and password.
    On successful authentication, a JSON Web Token (JWT) is returned in the
    response body.


    **HTTP Request** <br />
    `POST /accounts/login/`

    **Request Body Parameters**
      - username (*phone number or email*)
      - password

    **Response Body** <br />
    The response body returns the user data with *access* and *refresh* JWT
    tokens. The access token is used to perform HTTP operations on restricted
    resource. The refersh token is used to retrieve new access tokens when the
    existing token expires.

    **Token Expirations** <br />
    - Access Token: 60 minutes
    - Refresh Token: 90 days
    """
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        responses={
            200: UserResponseSerializer(),
            400: account_schema.login_400_response
        },
        operation_id='user-login',
        tags=['User Accounts']
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
        tags=['User Accounts']
    )
)
class UserRegistrationAPIView(CreateAPIView):
    """
    post:
    User Registration

    Register new users and create new user accounts for them.

    **HTTP Request** <br />
    `POST /accounts/register/`

    **Request Body Parameters** <br />
    - First Name
    - Last Name
    - Phone Number
    - Email Address
    - Password

    **Response Body** <br />
    The response body returns the new user data with *access* and *refresh* JWT
    tokens. The access token is used to perform HTTP operations on restricted
    resource. The refersh token is used to retrieve new access tokens when the
    existing token expires.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
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

    Check submitted email is a valid email address and not registered
    in the system.

    **HTTP Request** <br />
    `POST /accounts/email/validate/`

    **Request Body Parameters** <br />
    - Email

    **Response Body** <br />
    - Email
    """
    serializer_class = ValidEmailSerialzier

    @swagger_auto_schema(
        operation_id='email-validation',
        tags=['User Accounts'],
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

    Check submitted phone number is a valid phone number and not registered
    in the system.

    **HTTP Request** <br />
    `POST /accounts/phone/validate/`

    **Request Body Parameters** <br />
    - Phone Number

    **Response Body** <br />
    - Phone Number
    - One-Time Password (OTP)
    """
    serializer_class = ValidPhoneNumberSerialzier

    @swagger_auto_schema(
        operation_id='phone-number-validation',
        tags=['User Accounts'],
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
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.data['otp']
            sms = OTPSMS()
            sms.recipients = str(phone_number)
            sms.message = otp
            sms.send()
            return Response(serializer.data)

        error = {'phoneNumber': [_('Enter a valid phone number.')]}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(GenericAPIView):
    """
    post:
    Change Password

    Change password for authenticated users.

    **HTTP Request** <br />
    `POST /accounts/password/change/`

    **Request Body Parameters** <br />
    - Current Password
    - New Password
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAccountOwner]

    @swagger_auto_schema(
        operation_id='change-password',
        tags=['User Accounts'],
        responses={
            200: account_schema.password_change_200_response,
            400: account_schema.password_change_400_response,
            401: account_schema.unauthorized_401_response
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

    **HTTP Request** <br />
    `POST /accounts/token/verify/`
    """
    serializer_class = TokenVerifySerializer

    @swagger_auto_schema(
        operation_id='token-validation',
        responses={
            200: account_schema.token_validation_200_response,
            401: account_schema.token_validation_401_response
        },
        tags=['User Accounts']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    post:
    Token Referesh

    Returns new access token to replace an expired token.

    **HTTP Request** <br />
    `POST /accounts/token/refresh/`

    **Request Body Parameters** <br />
    - Refresh Token

    **Response Body** <br />
    - New Access Token
    """

    @swagger_auto_schema(
        operation_id='token-refresh',
        responses={
            200: account_schema.token_refresh_200_response,
            401: account_schema.token_refresh_401_response
        },
        tags=['User Accounts']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='user-detail',
        tags=['User Accounts'],
        responses={
            200: UserDetailSerializer(),
            401: account_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        operation_id='user-update',
        tags=['User Accounts'],
        responses={
            200: UserDetailSerializer(),
            400: account_schema.email_validation_400_response,
            401: account_schema.unauthorized_401_response,
            409: account_schema.email_validation_409_response,
        }
    )
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        operation_id='partial-user-update',
        tags=['User Accounts'],
        responses={
            200: UserDetailSerializer(),
            400: account_schema.email_validation_400_response,
            401: account_schema.unauthorized_401_response,
            409: account_schema.email_validation_409_response
        }
    )
)
class UserDetailAPIView(RetrieveUpdateAPIView):
    """
    get:
    User Detail

    Returns the user details for an authenticated account.

    **HTTP Request** <br />
    `GET /accounts/user/`

    **Response Body** <br />
    - User ID
    - Phone Number
    - Email Address
    - Active Boolean Flag
    - Profile Object
    - Settings Object

    put:
    User Update

    Updates the user details for an authenticated account.

    **Request Body Parameters** <br />
    - Email Address
    - Active Boolean Flag

    **HTTP Request** <br />
    `PUT /accounts/user/`

    **Response Body** <br />
    - User ID
    - Phone Number
    - Email Address
    - Active Boolean Flag
    - Profile Object
    - Settings Object

    patch:
    Partial User Update

    Partially updates the user details for an authenticated account.

    **Request Body Parameters** <br />
    - Email Address
    - Active Boolean Flag

    **HTTP Request** <br />
    `PATCH /accounts/user/`

    **Response Body** <br />
    - User ID
    - Phone Number
    - Email Address
    - Active Boolean Flag
    - Profile Object
    - Settings Object
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
        tags=['User Accounts'],
        responses={
            200: ProfileSerializer(),
            401: account_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        operation_id='user-profile-update',
        tags=['User Accounts'],
        responses={
            200: ProfileSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: account_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        operation_id='partial-user-profile-update',
        tags=['User Accounts'],
        responses={
            200: ProfileSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: account_schema.unauthorized_401_response
        }
    )
)
class UserProfileDetailAPIView(RetrieveUpdateAPIView):
    """
    get:
    User Profile Detail

    Returns the profile details of the current authenticated user.

    **HTTP Request** <br />
    `GET /accounts/user/profile/`

    **Response Body** <br />
    - First Name
    - Last Name
    - City
    - Country
    - Profile Photo
    - Last Update Date and Time

    put:
    User Profile Update

    Updates the profile details of the currently authenticated user.

    **HTTP Request** <br />
    `PUT /accounts/user/profile/`

    **Request Body Parameters** <br />
    - First Name (*required*)
    - Last Name (*required*)
    - City
    - Country
    - Profile Photo
    - Bio

    **Response Body** <br />
    - First Name
    - Last Name
    - City
    - Country
    - Profile Photo
    - Bio
    - Last Updated Date and Time

    patch:
    Partial User Profile Update

    Partially updates the profile details of the currently authenticated user.

    **HTTP Request** <br />
    `PATCH /accounts/user/profile/`

    **Request Body Parameters** <br />
    - First Name (*required*)
    - Last Name (*required*)
    - City
    - Country
    - Profile Photo
    - Bio

    **Response Body** <br />
    - First Name
    - Last Name
    - City
    - Country
    - Profile Photo
    - Bio
    - Last Updated Date and Time
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
        tags=['User Accounts'],
        responses={
            200: SettingSerializer(),
            401: account_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        operation_id='user-settings-update',
        tags=['User Accounts'],
        responses={
            200: SettingSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: account_schema.unauthorized_401_response
        }
    )
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        operation_id='partial-user-settings-update',
        tags=['User Accounts'],
        responses={
            200: SettingSerializer(),
            400: account_schema.user_profile_update_400_response,
            401: account_schema.unauthorized_401_response
        }
    )
)
class UserSettingsAPIView(RetrieveUpdateAPIView):
    """
    get:
    User Settings

    Returns the settings of the current authenticated user.

    **HTTP Request** <br />
    `GET /accounts/user/settings/`

    **Response Body** <br />
    - Currency
    - Last Update Date and Time

    put:
    User Settings Update

    Updates the settings of the currently authenticated user.

    **HTTP Request** <br />
    `PUT /accounts/user/settings/`

    **Request Body Parameters** <br />
    - Currency (*required*)

    **Response Body** <br />
    - Currency
    - Last Updated Date and Time

    patch:
    Partial User Settings Update

    Partially updates the settings of the currently authenticated user.

    **HTTP Request** <br />
    `PATCH /accounts/user/settings/`

    **Request Body Parameters** <br />
    - Currency (*required*)

    **Response Body** <br />
    - Currency (*required*)
    - Last Updated Date and Time
    """
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [IsSettingOwner]

    def get_object(self):
        return self.request.user.settings


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        operation_id='password-reset',
        tags=['User Accounts'],
        responses={
            200: PasswordResetSerializer(),
            400: account_schema.password_reset_400_response,
            404: account_schema.password_reset_404_response
        }
    )
)
class PasswordResetAPIView(CreateAPIView):
    """
    post:
    Password Reset

    Returns a one-time password (OTP) code to let users reset their
    forgotten password. It also sends the OTP code to the user mobile
    phone via SMS.

    **HTTP Request** <br />
    `POST /accounts/password/reset/`

    **Request Body Parameters** <br />
    - Phone Number

    **Response Body** <br />
    - Phone Number
    - OTP code (A 6-digit numeric code)
    - Expiration timestamp in milliseconds
    """
    queryset = PasswordResetCode.objects.all()
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(GenericAPIView):
    """
    post:
    Password Reset Confirm

    Resets a forgotten password using a one-time passowrds (OTP).

    **HTTP Request** <br />
    `POST /accounts/password/reset/confirm/`

    **Request Body Parameters** <br />
    - Phone Number
    - One-time Password (OTP)
    - New Password
    """
    queryset = PasswordResetCode.objects.all()
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id='password-reset-confirm',
        responses={
            200: account_schema.password_reset_confirm_200_response,
            400: account_schema.password_reset_confirm_400_response,
            404: account_schema.password_reset_confirm_404_response
        },
        tags=['User Accounts']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            message = {'detail': _('New password is set successfully.')}
            return Response(message)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
