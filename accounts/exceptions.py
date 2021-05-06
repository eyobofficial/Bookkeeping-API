from rest_framework.exceptions import APIException


class NonUniqueEmailException(APIException):
    status_code = 409
    default_detail = 'The email address is already registered.'
    default_code = 'non-unique-email'


class NonUniquePhoneNumberException(APIException):
    status_code = 409
    default_detail = 'The phone number is already registered.'
    default_code = 'non-unique-phone-number'
