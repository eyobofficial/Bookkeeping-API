from rest_framework import serializers

from drf_yasg import openapi
from phonenumber_field.serializerfields import PhoneNumberField


class CustomPhoneNumberField(PhoneNumberField):
    """
    Custom phone number field with a JSON serializable representation.
    """

    def to_representation(self, obj):
        return obj.as_e164


class TimestampField(serializers.Field):
    """
    A millisecond-based (JS-like) timestamp serializer field.
    """

    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_INTEGER,
        }

    def to_representation(self, obj, *args, **kwargs):
        return round(obj.timestamp() * 1000)
