from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.decorators import method_decorator
from django.core.validators import EmailValidator, ValidationError

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, \
    RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenVerifyView, \
    TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from accounts.utils.jwthandler import jwt_response_payload_handler
from accounts.schema.serializers import UserResponseSerializer
from .serializers import UserRegistrationSerializer, LoginSerializer, \
    ValidEmailSerialzier, ValidPhoneNumberSerialzier, PasswordChangeSerializer,\
    TokenVerifySerializer
from .sms.otp import OTPSMS
from .permissions import IsAccountOwner


User = get_user_model()

class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_summary='Sign in existing user',
        operation_description='''
            **Endpoint URI:** `POST /accounts/login/`

            The Dukka API uses JWT (JSON Web Token) for authenticating existing\
            users. The authentication is peformed by sending a `username` and \
            `password` fields via POST request. The `username` can either be \
            the user's phone number or email address.

            After a successful authentication, the user's account data and two \
            types of JWT tokes are returned in the response. These tokens are:

            #### 1. Access Token
            It is used to access restricted resources in subsequent requests. \
            When attempting to perform any HTTP actions on a restricted \
            resource, the access token must be sent in the `Authorization` \
            header of the request. The access token expires after 60 minutes.

            #### 2. Refresh Token
            When the access token expires after 5 minutes, the refresh token \
            should be used get new access token. The refresh token expires in \
            90 days.
        ''',
        responses={
            200: UserResponseSerializer(),
            400: openapi.Response(
                description='Incorrect username or password.',
                examples={
                    "application/json": {
                        "detail": "Wrong username or password"
                    }
                }

            )

        },
        operation_id='user-login',
        tags=['Accounts']
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
        operation_summary='Register new user',
        operation_description='''
        **Endpoint URI:** `POST /accounts/register/`
        ''',
        responses={
            '201': UserResponseSerializer(),
            '400': openapi.Response(
                description='Validation Errors',
                examples={
                    'application/json': {
                        'phone_number': ['Enter a valid phone number.'],
                        'email': ['Enter a valid email address.'],
                        'password': [
                            'This password is too short.',
                            'This password is too common.'
                        ]
                    }
                }

            ),
        },
        operation_id='user-registration',
        tags=['Accounts']
    )
)
class UserRegistrationAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # Validate serialized data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EmailValidatorAPIView(GenericAPIView):
    serializer_class = ValidEmailSerialzier

    @swagger_auto_schema(
        operation_id='validate-email',
        operation_summary='Validate Email',
        tags=['Accounts'],
        responses={
            '200': ValidEmailSerialzier(),
            '400': openapi.Response(
                description='Invalid Email Address',
                examples={
                    'application/json': {
                        'detail': 'Enter a valid email address.'
                    }
                }

            ),
            '409': openapi.Response(
                description='Duplicate Email Address',
                examples={
                    'application/json': {
                        'detail': 'The email address is already registered.'
                    }
                }

            ),
        },
        operation_description='''
        **Endpoint URI**: `POST /accounts/validate-email/`

        Check whether the email is:
        - Valid email address
        - Unique (i.e. not registered yet)
        '''
    )
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        error = {'detail': 'Enter a valid email address.'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberValidatorAPIView(GenericAPIView):
    serializer_class = ValidPhoneNumberSerialzier

    @swagger_auto_schema(
        operation_id='validate-phone-number',
        operation_summary='Validate Phone Number',
        tags=['Accounts'],
        responses={
            '200': ValidPhoneNumberSerialzier(),
            '400': openapi.Response(
                description='Invalid Phone Number',
                examples={
                    'application/json': {
                        'detail': 'Enter a valid phone number.'
                    }
                }

            ),
            '409': openapi.Response(
                description='Duplicate Phone Number',
                examples={
                    'application/json': {
                        'detail': 'The phone number is already registered.'
                    }
                }

            ),
        },
        operation_description='''
        **Endpoint URI**: `POST /accounts/validate-phone-number/`

        Check whether the phone number is:
        - Valid phone number
        - Unique (i.e. not registered yet)
        '''
    )
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Send OTP SMS
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.data['otp']
            sms = OTPSMS()
            sms.recipients = str(phone_number)
            sms.message = str(otp)
            sms.send()
            return Response(serializer.data)

        error = {'detail': 'Enter a valid phone number.'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(GenericAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAccountOwner]

    @swagger_auto_schema(
        operation_id='change-password',
        operation_summary='Change user password',
        tags=['Accounts'],
        responses={
            '200': openapi.Response(
                description='Password Changed Successfully.',
                examples={
                    'application/json': {
                        'detail': 'Password changed successfully.'
                    }
                }

            ),
            '400': openapi.Response(
                description='Validation Errors',
                examples={
                    'application/json': {
                        'new_password': [
                            ('This password is too short. '
                            'It must contain at least 8 characters.'),
                            'This password is too common.'
                        ],
                        'old_password': ['Wrong old password.']
                    }
                }

            ),
        },
        operation_description='''
        **Endpoint URI**: `POST /accounts/change-password/`

        Let authenticated users change their old password.
        '''
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(
            context={'user': user},
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            response = {'detail': 'Password changed successfully.'}
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenVerifyView(TokenVerifyView):
    serializer_class = TokenVerifySerializer

    @swagger_auto_schema(
        operation_summary='Verify JWT Access Token',
        operation_description='''
        **Endpoint URI:** `/accounts/token/verify/`

        Check if access token is valid and not expired.
        ''',
        responses={
            200: openapi.Response(
                description='Success',
                examples={
                    'application/json': {
                        'detail': 'Token is valid'
                    }
                }

            ),
            401: openapi.Response(
                description='Unauthorized',
                examples={
                    'application/json': {
                        'code': 'token_not_valid',
                        'detail': 'Token is invalid or expired.'
                    }
                }

            ),
        },
        tags=['Accounts']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)



class CustomTokenRefreshView(TokenRefreshView):

    @swagger_auto_schema(
        operation_summary='Refresh JWT Access Token',
        operation_description='''
        **Endpoint URI:** `/accounts/token/refresh/`
        ''',
        responses={
            200: openapi.Response(
                description='Success',
                examples={
                    'application/json': {
                        'access': 'string'
                    }
                }

            ),
            401: openapi.Response(
                description='Unauthorized',
                examples={
                    'application/json': {
                        'code': 'token_not_valid',
                        'detail': 'Token is invalid or expired.'
                    }
                }

            ),
        },
        tags=['Accounts']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
