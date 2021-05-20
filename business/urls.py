from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import BusinessTypeViewSet, BusinessAccountViewSet, \
    BusinessCustomerViewSet


app_name = 'business'


router = DefaultRouter()
router.register(r'', BusinessAccountViewSet)
router.register(r'types', BusinessTypeViewSet)
router.register(r'(?P<business_id>[0-9a-f-]+)/customers', BusinessCustomerViewSet)


urlpatterns = router.urls
