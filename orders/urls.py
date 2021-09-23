from rest_framework import routers

from .views import OrderItemViewSet


app_name = 'orders'


router = routers.DefaultRouter()
router.register(r'(?P<order_id>[0-9a-f-]+)/order-items', OrderItemViewSet)

urlpatterns = router.urls
