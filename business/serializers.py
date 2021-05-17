from rest_framework import serializers

from .models import BusinessType


class BusinessTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessType
        fields = ('id', 'title', )
