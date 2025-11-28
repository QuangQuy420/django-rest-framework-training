# apps/api/urls.py
from django.urls import path, include

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("blog/", include("apps.blog.urls")),
]
