from .views import MissionViewSet

from apps.core.routers import IntRouter



routeur = IntRouter()
routeur.register("missions", MissionViewSet, basename="mission")

urlpatterns = routeur.urls