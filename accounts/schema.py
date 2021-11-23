from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi
from django_countries import countries


# Example HTTP response with 401 status for user login view
login_401_response = openapi.Response(
    description=_('Unauthorized'),
    examples={
        'application/json': {
            'detail': _('Wrong username or password.')
        }
    }
)


# Example HTTP response with 403 status for user login view
login_403_response = openapi.Response(
    description=_('Permission Denied'),
    examples={
        'application/json': {
            'detail': _('User account is disabled.')
        }
    }
)


# Example HTTP response with 400 status for user registration view
registration_400_response = openapi.Response(
    description=_('Validation Errors'),
    examples={
        'application/json': {
            'phoneNumber': [_('Enter a valid phone number.')],
            'email': [_('Enter a valid email address.')],
            'password': [
                _('This password is too short.'),
                _('This password is too common.')
            ]
        }
    }
)


# Example HTTP response with 400 status for email validation view
email_validation_400_response = openapi.Response(
    description=_('Invalid Email Address'),
    examples={
        'application/json': {
            'email': [_('Enter a valid email address.')]
        }
    }
)


# Example HTTP response with 409 status for email validation view
email_validation_409_response = openapi.Response(
    description='Duplicate Email Address',
    examples={
        'application/json': {
            'detail': _('The email address is already registered.')
        }
    }
)


# Example HTTP response with 400 status for phone number validation view
phone_validation_400_response = openapi.Response(
    description=_('Invalid Phone Number'),
    examples={
        'application/json': {
            'phoneNumber': [_('Enter a valid phone number.')]
        }
    }
)


# Example HTTP response with 409 status for phone number validation view
phone_validation_409_response = openapi.Response(
    description=_('Duplicate Phone Number'),
    examples={
        'application/json': {
            'detail': _('The phone number is already registered.')
        }
    }
)


# Example HTTP response with 404 status when OTP (One-Time Password)
# is not found.
otp_not_found_404_response = openapi.Response(
    description=_('OTP Not Found'),
    examples={
        'application/json': {
            'detail': _('Wrong or expired OTP (One-time Password).')
        }
    }
)

# Example HTTP response with 200 status for phone number confirm view
phone_number_confirm_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'detail': _('Phone number successfully validated.')
        }
    }
)


# Example HTTP response with 200 status for password change view
password_change_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'detail': _('Password changed successfully.')
        }
    }
)


# Example HTTP response with 400 status for password change view
password_change_400_response = openapi.Response(
    description=_('Validation Errors'),
    examples={
        'application/json': {
            'newPassword': [
                _('This password is too short.It must contain at least 8 characters.'),
                _('This password is too common.')
            ],
            'currentPassword': [_('Wrong current password.')]
        }
    }
)


# Example HTTP response with 200 status for token validation view
token_validation_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'detail': _('Token is valid')
        }
    }
)


# Example HTTP response with 401 status for token validation view
token_validation_401_response = openapi.Response(
    description=_('Unauthorized'),
    examples={
        'application/json': {
            'code': 'token_not_valid',
            'detail': _('Token is invalid or expired.')
        }
    }
)


# Example HTTP response with 200 status for token refresh view
token_refresh_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'access': 'string'
        }
    }
)


# Example HTTP response with 401 status for token refresh view
token_refresh_401_response = openapi.Response(
    description=_('Unauthorized'),
    examples={
        'application/json': {
            'code': 'token_not_valid',
            'detail': _('Token is invalid or expired.')
        }
    }
)


# Example HTTP response with 404 status for password reset view
password_reset_404_response = openapi.Response(
    description=_('Account Not Found'),
    examples={
        'application/json': {
            'detail': _('The account is not registered.')
        }
    }
)


# Example HTTP response with 400 status for password reset view
password_reset_400_response = openapi.Response(
    description=_('Invalid Phone Number'),
    examples={
        'application/json': {
            'phoneNumber': [_('Enter a valid phone number.')]
        }
    }
)


# Example HTTP response with 200 status for password reset confirm view
password_reset_confirm_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'detail': _('New password is set successfully.')
        }
    }
)


# Example HTTP response with 400 status for password reset confirm view
password_reset_confirm_400_response = openapi.Response(
    description=_('Invalid Phone Number'),
    examples={
        'application/json': {
            'phoneNumber': [_('Enter a valid phone number.')],
            'pin': [
                _('Value should be digits.'),
                _('Ensure this field has no more than 4 characters.'),
                _('Ensure this field has at least 4 characters.')
            ]
        }
    }
)


# Example HTTP response with 404 status for password reset confirm view
password_reset_confirm_404_response = openapi.Response(
    description=_('Invalid Code'),
    examples={
        'application/json': {
            'detail': _('Invalid or expired code.')
        }
    }
)


# Example HTTP response with 400 status for user proflie update view
user_profile_update_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'firstName': [_('This field may not be blank.')],
            'lastName': [_('This field may not be blank.')]
        }
    }
)


# Example HTTP response with 400 status for user proflie update view
user_business_account_create_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'name': [_('This field may not be blank.')],
            'businessType': [
                _('This field may not be blank.'),
                _('Invalid pk 99 - object does not exist.')
            ],
            'country': [_('"EX" is not a valid choice')]
        }
    }
)


# Sample Request body for User Profile Edit Endpoints
profile_edit_request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['firstName', 'lastName'],
    properties={
        'firstName': openapi.Schema(type=openapi.TYPE_STRING, max_length=100),
        'lastName': openapi.Schema(type=openapi.TYPE_STRING, max_length=100),
        'address': openapi.Schema(type=openapi.TYPE_STRING),
        'city': openapi.Schema(type=openapi.TYPE_STRING, max_length=100),
        'postalCode': openapi.Schema(type=openapi.TYPE_STRING, max_length=10),
        'country': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=[country[0] for country in countries]
        ),
        'profilePhoto': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description=_('The ID of the photo instance to be uploaded.')
        ),
    }
)
