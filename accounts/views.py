from django.contrib.auth import get_user_model, authenticate
from django.utils.decorators import method_decorator
from django.core.validators import EmailValidator, ValidationError

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from accounts.utils.jwthandler import jwt_response_payload_handler
from .serializers import UserSerializer, LoginSerializer, UserResponseSerializer, \
    ValidEmailSerialzier, ValidPhoneNumberSerialzier
from .sms.otp import OTPSMS


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
            header of the request. The access token expires after 5 minutes.

            #### 2. Refresh Token
            When the access token expires after 5 minutes, the refresh token \
            should be used get new access token. The refresh token expires in \
            30 days.
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
        tags=['User Login']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                token = RefreshToken.for_user(user)
                data = {
                    'refresh': str(token),
                    'access': str(token.access_token)
                }
                return Response(data, status=status.HTTP_200_OK)
            return Response(
                {'detail': 'Wrong Username or Password'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        tags=['User Registration']
    )
)
class UserRegistrationAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # Validate serialized data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create new user
        user = serializer.save()

        # Generate access & refresh token
        token = RefreshToken.for_user(user)
        data = jwt_response_payload_handler(token, user, request)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class EmailValidatorAPIView(GenericAPIView):
    serializer_class = ValidEmailSerialzier

    @swagger_auto_schema(
        operation_id='validate-email',
        operation_summary='Validate Email',
        tags=['Email Validation'],
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
        tags=['Phone Number Validation'],
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
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        password1 = request.data.get('password1')
        password2 = request.data.get('password1')
