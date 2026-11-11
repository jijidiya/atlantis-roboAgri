from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DecisionViewSet, DecisionZoneView, IrrigationViewSet

routeur = DefaultRouter()
routeur.register("irrigations", IrrigationViewSet, basename="irrigation")
routeur.register("decisions", DecisionViewSet, basename="decision")

urlpatterns = routeur.urls + [
    path("zones/<int:zone_id>/decision/", DecisionZoneView.as_view(), name="zone-decision"),
]