from django.conf import settings
from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi
from django_countries import countries

from inventory.units import MeasurementUnit


PHONENUMBER_COUNTRY = countries.name(settings.PHONENUMBER_DEFAULT_REGION)

measurement_unit = MeasurementUnit()


# Sample request body for customer create/update endpoints
customer_edit_request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name'],
    properties={
        'name': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=100,
            description=_('Name of the customer.')
        ),
        'phoneNumber': openapi.Schema(
            type=openapi.TYPE_STRING,
            description=_(
                'The customer phone number in any recognizable format. '
                f'If the phone number is a *{PHONENUMBER_COUNTRY}* number, '
                'country code is not required. Otherwise, include the country code prefix.'
            )
        ),
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            max_length=255
        ),
        'photo': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description=_('The ID of the photo instance to be uploaded.')
        ),
    }
)


# Example HTTP response with 415 status for photo upload view
duplicate_409_response = openapi.Response(
    description=_('Duplicate Customer'),
    examples={
        'application/json': {
            'nonFieldErrors': [
                _('A customer with this phone numuber (email address) is registered.')
            ]
        }
    }
)


# Example HTTP response with 200 status for order detail view
order_detail_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'id': '497f6eca-6276-4993-bfeb-53cbbbba6f08',
            'orderType': 'FROM_LIST',
            'customer': {
                'id': '497f6eca-6276-4993-bfeb-53cbbbba6f08',
                'name': 'string',
                'phoneNumber': 'string',
                'email': 'user@example.com',
                'photo': 'facac570-5bc6-468f-9351-d5126403b854'
            },
            'description': 'string',
            'status': 'OPEN',
            'orderItems': [
                {
                    'id': '497f6eca-6276-4993-bfeb-53cbbbba6f08',
                    'product': 'string',
                    'quantity': 0,
                    'unit': 'pc',
                    'price': 0,
                    'cost': 0,
                    'updatedAt': '2019-08-24T14:15:22Z'
                }
            ],
            'cost': 0,
            'taxPercentage': 0.15,
            'taxAmount': 0,
            'totalAmount': 0,
            'createdAt': '2019-08-24T14:15:22Z',
            'updatedAt': '2019-08-24T14:15:22Z'
        }
    }
)

# Sample Request Body for Stock Objects
stock_request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['product', 'unit', 'quantity', 'price'],
    properties={
        'product': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=100,
            description=_('Name of the product.')
        ),
        'unit': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=measurement_unit.all_units,
            description=_('Unit of measurement.')
        ),
        'quantity': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description=_('The amount of quantity left in the stock.')
        ),
        'price': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description=_('The price of the stock item per unit.')
        ),
        'photo': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description=_('The ID of the photo instance to be uploaded.')
        ),
    }
)
