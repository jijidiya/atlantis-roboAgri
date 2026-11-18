"""Routes de l'API « communication » : endpoints réservés au robot."""
from django.urls import path

from .views import MessageRobotView, MissionSuivanteView


urlpatterns = [
    path("robot/messages/", MessageRobotView.as_view(), name="robot-messages"),
    path("robot/mission-suivante/", MissionSuivanteView.as_view(), name="robot-mission-suivante"),
]