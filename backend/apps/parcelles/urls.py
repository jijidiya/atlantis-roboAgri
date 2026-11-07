from rest_framework.routers import DefaultRouter

from .views import CultiverViewSet, CultureViewSet, ParcelleViewSet, ZoneViewSet

router = DefaultRouter()
router.register("parcelles", ParcelleViewSet)
router.register("zones", ZoneViewSet)
router.register("cultures", CultureViewSet)
router.register("cultivers", CultiverViewSet)

urlpatterns = router.urls
