from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from apps.blog.permissions import IsAuthorOrReadOnly
from .models import Post
from .serializers import PostSerializer

class PostPagination(PageNumberPagination):
    page_size = 10


class PostViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Post:
      - GET    /api/blog/        -> list posts
      - POST   /api/blog/        -> create post
      - GET    /api/blog/{id}/   -> retrieve post
      - PUT    /api/blog/{id}/   -> full update
      - PATCH  /api/blog/{id}/   -> partial update
      - DELETE /api/blog/{id}/   -> delete post
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = PostPagination

    def get_queryset(self): 
        return (
            Post.objects
            .select_related("author")
            .prefetch_related(
                "reactions",
                "comments__author",
                "comments__reactions",
                "comments__replies__author",
                "comments__replies__reactions",
            )
        )

    def perform_create(self, serializer):
        """
        Called when POST /api/blog/ is used.
        We set the author to the currently logged-in user.
        Client only needs to send title + content.
        """
        serializer.save(author=self.request.user)
