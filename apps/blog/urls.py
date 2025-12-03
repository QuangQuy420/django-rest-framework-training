# apps/blog/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PostViewSet, ReactionViewSet

router = DefaultRouter()
router.register(r"", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"reactions", ReactionViewSet, basename="reaction")

urlpatterns = [
    path("", include(router.urls)),
]
