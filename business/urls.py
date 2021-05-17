from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import BusinessTypeViewSet


app_name = 'business'


router = DefaultRouter()
router.register(r'types', BusinessTypeViewSet)


urlpatterns = router.urls
