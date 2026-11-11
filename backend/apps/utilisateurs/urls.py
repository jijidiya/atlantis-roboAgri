
from django.urls import path

from .views import (
    ConnexionAPIView,
    RafraichissementAPIView,
    MoiAPIView,
)

urlpatterns = [
    path(
        "connexion/",
        ConnexionAPIView.as_view(),
        name="auth-connexion"
    ),
    path(
        "rafraichir/",
        RafraichissementAPIView.as_view(),
        name="auth-rafraichir"
    ),
    path(
        "moi/",
        MoiAPIView.as_view(),
        name="auth-moi"
    ),
]