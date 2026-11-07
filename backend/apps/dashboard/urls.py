from django.urls import path

from .views import EvolutionHumiditeView, ResumeView

urlpatterns = [
    path("dashboard/resume/", ResumeView.as_view()),
    path("dashboard/zones/<int:zone_id>/humidite/", EvolutionHumiditeView.as_view()),
]
