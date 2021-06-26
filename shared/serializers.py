from rest_framework import serializers

from .models import PhotoUpload


class PhotoUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhotoUpload
        fields = ('id', 'photo', 'created_at')
