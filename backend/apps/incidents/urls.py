from .views import IncidentViewSet

from apps.core.routers import IntRouter


routeur = IntRouter()
routeur.register("incidents", IncidentViewSet, basename="incident")

urlpatterns = routeur.urls