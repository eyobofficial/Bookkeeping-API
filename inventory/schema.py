from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi


# Example HTTP response with 404 status for password reset view
barcode_number_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'barcodeNumber': [_('This field is required.')]
        }
    }
)
