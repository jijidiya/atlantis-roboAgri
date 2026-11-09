from rest_framework.routers import DefaultRouter

from .views import MissionViewSet

routeur = DefaultRouter()
routeur.register("missions", MissionViewSet, basename="mission")

urlpatterns = routeur.urls