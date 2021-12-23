from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi


barcode_number_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'barcodeNumber': [_('This field is required.')]
        }
    }
)


restock_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'restockedQuantity': [_('Restocked quantity must be greater than zero.')]
        }
    }
)
