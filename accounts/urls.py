from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_auth.views import UserDetailsView

from .views import UserRegistrationAPIView, EmailValidatorAPIView, \
    PhoneNumberValidatorAPIView, LoginAPIView, PasswordChangeView


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
    path('users/me/', UserDetailsView.as_view(), name='user'),
    path(
        'change-password/',
        PasswordChangeView.as_view(),
        name='change-password'
    )
    # path('', include('rest_auth.urls')),
]
