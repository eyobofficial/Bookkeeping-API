from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def is_digit(value):
    if not value.isdigit():
        raise serializers.ValidationError(_('Value should be digits.'))
