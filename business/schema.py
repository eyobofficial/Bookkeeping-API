from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi


# Example HTTP response with 200 status for customer photo upload view
customer_photo_upload_200_response = openapi.Response(
    description=_('Success'),
    examples={
        'application/json': {
            'detail': _('Customer photo is uploaded.')
        }
    }
)


# Example HTTP response with 400 status for customer photo upload view
customer_photo_upload_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'detail': _('No image file included.')
        }
    }
)


# Example HTTP response with 415 status for customer photo upload view
customer_photo_upload_415_response = openapi.Response(
    description=_('Unsupported Media Type'),
    examples={
        'application/json': {
            'detail': _('Unsupported file type.')
        }
    }
)


# Example HTTP response with 204 status for customer photo remove view
customer_photo_remove_204_response = openapi.Response(
    description=_('No Content'),
    examples={
        'application/json': {
            'detail': _('Customer photo is deleted.')
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
            'createdAt': '2019-08-24T14:15:22Z',
            'updatedAt': '2019-08-24T14:15:22Z'
        }
    }
)
