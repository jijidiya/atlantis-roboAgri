"""Routes des mesures."""

from rest_framework.routers import DefaultRouter

from .views import MesureHumiditeViewSet

router = DefaultRouter()
router.register("mesures", MesureHumiditeViewSet)

urlpatterns = router.urls
