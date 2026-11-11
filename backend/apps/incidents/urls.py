from rest_framework.routers import DefaultRouter

from .views import IncidentViewSet

routeur = DefaultRouter()
routeur.register("incidents", IncidentViewSet, basename="incident")

urlpatterns = routeur.urls