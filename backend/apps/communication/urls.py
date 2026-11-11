from django.urls import path

from .serializers import MessageRobotView, MissionSuivanteView

urlpatterns = [
    path("robot/messages/", MessageRobotView.as_view(), name="robot-messages"),
    path("robot/mission-suivante/", MissionSuivanteView.as_view(), name="robot-mission-suivante"),
]