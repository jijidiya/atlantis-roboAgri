from rest_framework.routers import DefaultRouter

from .views import MesureViewSet

routeur = DefaultRouter()
routeur.register("mesures", MesureViewSet, basename="mesure")

urlpatterns = routeur.urls