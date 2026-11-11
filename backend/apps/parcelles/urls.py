from rest_framework.routers import DefaultRouter

from .views import CultureViewSet, ParcelleViewSet, ZoneViewSet

routeur = DefaultRouter()
routeur.register("parcelles", ParcelleViewSet, basename="parcelle")
routeur.register("zones", ZoneViewSet, basename="zone")
routeur.register("cultures", CultureViewSet, basename="culture")

urlpatterns = routeur.urls