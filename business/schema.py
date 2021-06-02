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
