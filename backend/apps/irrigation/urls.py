from django.urls import path

from .views import DecisionViewSet, DecisionZoneView, IrrigationViewSet
from apps.core.routers import IntRouter


routeur = IntRouter()

routeur.register("irrigations", IrrigationViewSet, basename="irrigation")
routeur.register("decisions", DecisionViewSet, basename="decision")

urlpatterns = routeur.urls + [
    path("zones/<int:zone_id>/decision/", DecisionZoneView.as_view(), name="zone-decision"),
]