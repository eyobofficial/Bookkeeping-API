from rest_framework import serializers

from django_countries.serializers import CountryFieldMixin

from customers.models import Customer

from .models import BusinessType, BusinessAccount


class BusinessTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessType
        fields = ('id', 'title', )


class BusinessAccountSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = BusinessAccount
        fields = '__all__'


class BusinessCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = (
            'id', 'name', 'phone_number',
            'email', 'created_at', 'updated_at'
        )
