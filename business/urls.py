from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views.business_accounts import BusinessTypeViewSet, BusinessAccountViewSet
from .views.business_customers import BusinessCustomerViewSet
from .views.business_expenses import BusinessExpenseViewSet
from .views.business_inventory import BusinessStockViewSet


app_name = 'business'


router = DefaultRouter()
router.register(r'types', BusinessTypeViewSet)
router.register(r'(?P<business_id>[0-9a-f-]+)/customers', BusinessCustomerViewSet)
router.register(r'(?P<business_id>[0-9a-f-]+)/expenses', BusinessExpenseViewSet)
router.register(
    r'(?P<business_id>[0-9a-f-]+)/inventory/stocks',
    BusinessStockViewSet
)
router.register(r'', BusinessAccountViewSet)  # Must be at the bottom

urlpatterns = router.urls
