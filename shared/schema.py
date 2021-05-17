from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi


# Sample HTTP response with 401 Unauthorized statuses
unauthorized_401_response = openapi.Response(
    description=_('Unauthorized'),
    examples={
        'application/json': {
            'detail': _('Authentication credentials were not provided.')
        }
    }
)
