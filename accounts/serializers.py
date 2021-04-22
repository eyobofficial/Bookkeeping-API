from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers
from allauth.account.adapter import get_adapter
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .fields import CustomPhoneNumberField


User = get_user_model()



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=120,
        write_only=True,
        style={'input_type': 'password'}
    )
    phone_number = CustomPhoneNumberField(
        required=True,
        error_messages={
            'invalid': 'Enter a valid phone number.'
        }
    )

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email',
            'password', 'first_name', 'last_name'
        )

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def create(self, validated_data):
        raw_password = validated_data['password']
        user = User(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        user.set_password(raw_password)
        user.save()
        return user
