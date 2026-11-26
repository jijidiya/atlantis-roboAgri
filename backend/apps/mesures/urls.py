from .views import MesureViewSet

from apps.core.routers import IntRouter


routeur = IntRouter()
routeur.register("mesures", MesureViewSet, basename="mesure")

urlpatterns = routeur.urls