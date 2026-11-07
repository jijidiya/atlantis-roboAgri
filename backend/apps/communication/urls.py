from django.urls import path

from .api import (
    EtatRobotView,
    MessagesRobotView,
    MissionRobotView,
    SyncRobotView,
)

# Chemins sans barre finale, exactement ceux de docs/protocole.md (section 5.2).
urlpatterns = [
    path("robot/mission", MissionRobotView.as_view()),
    path("robot/messages", MessagesRobotView.as_view()),
    path("robot/messages/sync", SyncRobotView.as_view()),
    path("robot/etat", EtatRobotView.as_view()),
]
