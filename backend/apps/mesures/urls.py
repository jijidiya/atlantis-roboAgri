from rest_framework.routers import DefaultRouter

from .views import MesureViewSet

router = DefaultRouter()
router.register("mesures", MesureViewSet)

urlpatterns = router.urls
