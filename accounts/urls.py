from django.urls import path

from rest_framework_jwt.views import ObtainJSONWebToken

from .views import UserRegistrationAPIView


app_name = 'accounts'


urlpatterns = [
    path('login/', ObtainJSONWebToken.as_view(), name='login'),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
]
