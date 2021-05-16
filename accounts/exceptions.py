from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import APIException


class NonUniqueEmailException(APIException):
    status_code = 409
    default_detail = _('The email address is already registered.')
    default_code = 'non-unique-email'


class NonUniquePhoneNumberException(APIException):
    status_code = 409
    default_detail = _('The phone number is already registered.')
    default_code = 'non-unique-phone-number'


class AccountNotRegisteredException(APIException):
    status_code = 404
    default_detail = _('The account is not registered.')
    default_code = 'non-registered-account'


class InvalidCodeException(APIException):
    status_code = 404
    default_detail = _('Invalid or expired code.')
    default_code = 'invalid-code'


class AccountDisabledException(APIException):
    status_code = 401
    default_detail = _('User account is disabled.')
    default_code = 'account-disabled'


class InvalidCredentialsException(APIException):
    status_code = 404
    default_detail = _('Wrong username or password.')
    default_code = 'invalid-credentials'
