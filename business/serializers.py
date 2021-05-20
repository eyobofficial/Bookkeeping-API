from rest_framework import serializers

from django_countries.serializers import CountryFieldMixin

from .models import BusinessType, BusinessAccount


class BusinessTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessType
        fields = ('id', 'title', )



class BusinessAccountSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = BusinessAccount
        fields = '__all__'
