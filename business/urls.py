from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import BusinessTypeViewSet, BusinessAccountViewSet, \
    BusinessCustomerViewSet, BusinessExpenseViewSet, BusinessStockViewSet


app_name = 'business'


router = DefaultRouter()
router.register(r'', BusinessAccountViewSet)
router.register(r'types', BusinessTypeViewSet)
router.register(r'(?P<business_id>[0-9a-f-]+)/customers', BusinessCustomerViewSet)
router.register(r'(?P<business_id>[0-9a-f-]+)/expenses', BusinessExpenseViewSet)
router.register(
    r'(?P<business_id>[0-9a-f-]+)/inventory/stocks',
    BusinessStockViewSet
)

urlpatterns = router.urls
