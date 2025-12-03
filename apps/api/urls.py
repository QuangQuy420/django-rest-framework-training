# apps/api/urls.py
from django.urls import include, path

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("blog/", include("apps.blog.urls")),
]
