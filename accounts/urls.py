from django.urls import path, include

from drf_yasg.utils import swagger_auto_schema

from .views import LoginAPIView, UserRegistrationAPIView, \
    EmailValidatorAPIView, PhoneNumberValidatorAPIView, PasswordChangeView, \
    CustomTokenRefreshView, CustomTokenVerifyView


app_name = 'accounts'


urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path(
        'validate-email/',
        EmailValidatorAPIView.as_view(),
        name='validate-email'
    ),
    path(
        'validate-phone-number/',
        PhoneNumberValidatorAPIView.as_view(),
        name='validate-phone-number'
    ),
    path(
        'change-password/',
        PasswordChangeView.as_view(),
        name='change-password'
    ),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token-verify'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]

