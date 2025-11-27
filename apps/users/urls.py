from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import CookieTokenObtainPairView, RegisterView, MeView

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="jwt-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Current user
    path("me/", MeView.as_view(), name="user-me"),
]
