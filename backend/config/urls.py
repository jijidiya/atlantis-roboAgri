"""Routes principales du projet."""
from django.contrib import admin
from django.urls import include, path

# Préfixe commun de l'API (api-frontend-backend.pdf §2, architecture.pdf §8.1).
API = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API}auth/", include("apps.utilisateurs.urls")),
    path(API, include("apps.parcelles.urls")),
    path(API, include("apps.missions.urls")),
    path(API, include("apps.mesures.urls")),
    path(API, include("apps.incidents.urls")),
    path(API, include("apps.irrigation.urls")),
    path(API, include("apps.communication.urls")),   # /robot/messages/ et /robot/mission-suivante/
]