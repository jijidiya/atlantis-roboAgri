"""Routes principales du projet."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Préfixe commun de l'API (api-frontend-backend.pdf §2, architecture.pdf §8.1).
API = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Documentation OpenAPI ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # --- Routes de l'API ---
    path(f"{API}auth/", include("apps.utilisateurs.urls")),
    path(API, include("apps.parcelles.urls")),
    path(API, include("apps.missions.urls")),
    path(API, include("apps.mesures.urls")),
    path(API, include("apps.incidents.urls")),
    path(API, include("apps.irrigation.urls")),
    path(API, include("apps.communication.urls")),   
]