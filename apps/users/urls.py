from django.urls import path

from .views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
    RegisterView,
)

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="jwt-login"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="jwt-logout"),
    path("me/", MeView.as_view(), name="user-me"),
]
