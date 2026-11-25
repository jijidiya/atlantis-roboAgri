from .views import CultureViewSet, ParcelleViewSet, ZoneViewSet

from apps.core.routers import IntRouter


routeur = IntRouter()
routeur.register("parcelles", ParcelleViewSet, basename="parcelle")
routeur.register("zones", ZoneViewSet, basename="zone")
routeur.register("cultures", CultureViewSet, basename="culture")

urlpatterns = routeur.urls