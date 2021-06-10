from django.urls import path, include

from rest_framework.routers import DefaultRouter

from business.views import business_accounts, business_customers, \
    business_expenses, business_inventory,  business_orders


app_name = 'business'


# Routers
router = DefaultRouter()
router.register(r'types', business_accounts.BusinessTypeViewSet)
router.register(
    r'(?P<business_id>[0-9a-f-]+)/customers',
    business_customers.BusinessCustomerViewSet
)
router.register(
    r'(?P<business_id>[0-9a-f-]+)/expenses',
    business_expenses.BusinessExpenseViewSet
)
router.register(
    r'(?P<business_id>[0-9a-f-]+)/inventory/stocks',
    business_inventory.BusinessStockViewSet
)

# Must be at the bottom to match '' pattern
router.register(r'', business_accounts.BusinessAccountViewSet)


# URL Confs
urlpatterns = [
    path(
        '<uuid:business_id>/orders/',
        business_orders.OrderListView.as_view(),
        name='order-list'
    ),
    path(
        '<uuid:business_id>/orders/from-list/',
        business_orders.InventoryOrderCreateView.as_view(),
        name='order-create-from-list'
    ),
    path(
        '<uuid:business_id>/orders/<uuid:pk>/from-list/',
        business_orders.InventoryOrderUpdateView.as_view(),
        name='order-update-from-list'
    ),
    path(
        '<uuid:business_id>/orders/custom/',
        business_orders.CustomOrderCreateView.as_view(),
        name='order-create-custom'
    ),
    path(
        '<uuid:business_id>/orders/<uuid:pk>/custom/',
        business_orders.CustomOrderUpdateView.as_view(),
        name='order-update-custom'
    ),
    path(
        '<uuid:business_id>/orders/<uuid:pk>/',
        business_orders.OrderDetailView.as_view(),
        name='order-detail'
    ),
    path('', include(router.urls)),
]
