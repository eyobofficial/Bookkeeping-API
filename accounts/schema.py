from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi


# Example HTTP response with 400 status for user login view
login_400_response = openapi.Response(
    description=_('Incorrect Username or Password.'),
    examples={
        'application/json': {
            'detail': _('Wrong username or password')
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
