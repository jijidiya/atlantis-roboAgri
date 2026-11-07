from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.parcelles.urls")),
    path("api/", include("apps.missions.urls")),
    path("api/", include("apps.mesures.urls")),
    path("api/", include("apps.irrigation.urls")),
    path("api/", include("apps.dashboard.urls")),
    path("api/", include("apps.communication.urls")),
]
