from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import NotFound

from .serializers import PhotoUploadSerializer
from .models import PhotoUpload


class PhotoUploadField(PhotoUploadSerializer):
    """
    Serializer field for PhotoUpload relational fields.

    - During serialization, it return the `photo` object of
    the serialized instance.
    - During deserialization, it accepts the primary key of the
    instance object.
    """

    def to_internal_value(self, pk):
        try:
            photo = PhotoUpload.objects.get(pk=pk)
        except PhotoUpload.DoesNotExist:
            error_message = _('Uploaded Photo Not Found')
            raise NotFound(detail=error_message)

        request = self.context['request']
        serializer = PhotoUploadSerializer(photo, context={'request': request})
        return serializer.data
