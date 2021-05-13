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
