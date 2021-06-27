from rest_framework import serializers

from .models import PhotoUpload


class PhotoUploadSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = PhotoUpload
        fields = ('id', 'photo_url', 'created_at')

    def get_photo_url(self, obj):
        """
        Returns the absolute URL path of the photo.
        """
        return self.context['request'].build_absolute_uri(obj.photo.url)

