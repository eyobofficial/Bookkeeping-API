from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from .serializers import UserRegistrationSerializer


User = get_user_model()

class UserRegistrationAPIView(CreateAPIView):
    """
    Register new users.

    `POST`: create a new user
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # Validate serialized data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create new user
        user = serializer.save()

        # Include user data along with token
        data = serializer.data
        return Response(serializer.data, status=status.HTTP_201_CREATED)
