from django.urls import path

from .api import MessageRobotView

urlpatterns = [path("robot/messages/", MessageRobotView.as_view())]
