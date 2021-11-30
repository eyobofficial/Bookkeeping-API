from rest_framework import serializers

from .models import Barcode


class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcode
        fields = ('id', 'code', 'product_name', 'description', 'product_photo')


class BarcodeFindSerializer(serializers.Serializer):
    barcode_number = serializers.CharField(max_length=255)
