from django.urls import path, include

from .views import UserLoginAPIView, UserRegistrationAPIView, \
    EmailValidatorAPIView, PhoneNumberValidatorAPIView, PasswordChangeView, \
    CustomTokenRefreshView, CustomTokenVerifyView, UserDetailAPIView, \
    PasswordResetAPIView, PasswordResetConfirmAPIView


app_name = 'accounts'


urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path(
        'email/validate/',
        EmailValidatorAPIView.as_view(),
        name='validate-email'
    ),
    path(
        'phone/validate/',
        PhoneNumberValidatorAPIView.as_view(),
        name='validate-phone-number'
    ),
    path(
        'password/change/',
        PasswordChangeView.as_view(),
        name='change-password'
    ),
    path(
        'password/reset/',
        PasswordResetAPIView.as_view(),
        name='password-reset'
    ),
    path(
        'password/reset/confirm/',
        PasswordResetConfirmAPIView.as_view(),
        name='password-reset-confirm'
    ),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token-verify'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('user/', UserDetailAPIView.as_view(), name='user-detail'),
]

