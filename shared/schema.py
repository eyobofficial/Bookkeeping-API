from django.utils.translation import gettext_lazy as _

from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema

from .badges import app_badge


class BadgesAutoSchema(SwaggerAutoSchema):
    def get_badges(self):
        return self.overrides.get('badges', [app_badge])

    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys)
        operation['x-badges'] = self.get_badges()
        return operation


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        swagger = super().get_schema(request, public)
        return swagger


# Sample HTTP response with 401 Unauthorized statuses
unauthorized_401_response = openapi.Response(
    description=_('Unauthorized'),
    examples={
        'application/json': {
            'detail': _('Authentication credentials were not provided.')
        }
    }
)


# Sample HTTP response with 404 Not Found statuses
not_found_404_response = openapi.Response(
    description=_('Not Found'),
    examples={
        'application/json': {
            'detail': _('Not found.')
        }
    }
)


# Sample HTTP response with 404 Not Found statuses for photos
photo_not_found_404_response = openapi.Response(
    description=_('Not Found'),
    examples={
        'application/json': {
            'detail': _('Uploaded Photo Not found.')
        }
    }
)


# Example HTTP response with 400 status for photo upload view
photo_upload_400_response = openapi.Response(
    description=_('Validation Error'),
    examples={
        'application/json': {
            'detail': _('No image file included.')
        }
    }
)


# Example HTTP response with 415 status for photo upload view
photo_upload_415_response = openapi.Response(
    description=_('Unsupported Media Type'),
    examples={
        'application/json': {
            'detail': _('Unsupported file type.')
        }
    }
)
