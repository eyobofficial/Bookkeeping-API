from rest_framework import routers

from .views import BarcodeViewSet


app_name = 'inventory'


router = routers.DefaultRouter()
router.register(r'barcodes', BarcodeViewSet)

urlpatterns = router.urls
