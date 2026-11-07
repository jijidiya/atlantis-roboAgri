from rest_framework.routers import DefaultRouter

from .views import IncidentViewSet, IrrigationViewSet

router = DefaultRouter()
router.register("irrigations", IrrigationViewSet)
router.register("incidents", IncidentViewSet)

urlpatterns = router.urls
