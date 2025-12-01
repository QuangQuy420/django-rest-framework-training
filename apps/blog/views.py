from rest_framework import viewsets, permissions, mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.blog.permissions import IsAuthorOrReadOnly
from django.contrib.contenttypes.models import ContentType
from .models import Post, Comment, Reaction
from .serializers import CommentSerializer, PostSerializer, ReactionSerializer

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
        serializer.save(author=self.request.user)

    # helper methods for comments on this post
    def _get_post_comments(self, post, request):
        comments = (
            post.comments
            .filter(parent__isnull=True)
            .select_related("author")
            .prefetch_related(
                "reactions",
                "replies__author",
                "replies__reactions",
            )
        )

        return CommentSerializer(
            comments,
            many=True,
            context={
                "request": request,
                "depth": 0,
                "max_depth": 5,
            },
        )

    def _create_post_comment(self, post, request):
        data = request.data.copy()
        data["post"] = post.id  # always bind to this post

        serializer = CommentSerializer(
            data=data,
            context={"request": request, "post": post},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return serializer

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="comments",
        permission_classes=[permissions.IsAuthenticated]
    )
    def comments(self, request, pk=None):
        """
        - GET  /api/blog/{post_id}/comments/  -> list top-level comments for this post
        - POST /api/blog/{post_id}/comments/  -> create comment or reply for this post
        """
        post = self.get_object()

        if request.method == "GET":
            serializer = self._get_post_comments(post, request)
            return Response(serializer.data)

        # POST
        serializer = self._create_post_comment(post, request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # helper methods for reactions on this post
    def _get_post_reactions(self, post, request):
        ct = ContentType.objects.get_for_model(Post)
        reactions = (
            Reaction.objects
            .filter(content_type=ct, object_id=post.id)
            .select_related("author")
        )
        return ReactionSerializer(
            reactions,
            many=True,
            context={"request": request},
        )

    def _create_post_reaction(self, post, request):
        serializer = ReactionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        ct = ContentType.objects.get_for_model(Post)
        Reaction.objects.create(
            author=request.user,
            content_type=ct,
            object_id=post.id,
            type=serializer.validated_data["type"],
        )

        # return same serializer (with validated type)
        return serializer

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="reactions",
        permission_classes=[permissions.IsAuthenticated]
    )
    def reactions(self, request, pk=None):
        """
        - GET  /api/blog/{post_id}/reactions/  -> list reactions on this post
        - POST /api/blog/{post_id}/reactions/  -> create reaction on this post
        """
        post = self.get_object()

        if request.method == "GET":
            serializer = self._get_post_reactions(post, request)
            return Response(serializer.data)

        serializer = self._create_post_reaction(post, request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Only update & delete comment:
      - PATCH /api/blog/comments/{id}/   -> update comment content
      - DELETE /api/blog/comments/{id}/  -> delete comment
    """
    queryset = Comment.objects.select_related("author", "post", "parent")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    # Only allow these HTTP methods for this ViewSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # helper methods for reactions on this comment
    def _get_comment_reactions(self, comment, request):
        ct = ContentType.objects.get_for_model(Comment)
        reactions = (
            Reaction.objects
            .filter(content_type=ct, object_id=comment.id)
            .select_related("author")
        )
        return ReactionSerializer(
            reactions,
            many=True,
            context={"request": request},
        )

    def _create_comment_reaction(self, comment, request):
        serializer = ReactionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        ct = ContentType.objects.get_for_model(Comment)
        Reaction.objects.create(
            author=request.user,
            content_type=ct,
            object_id=comment.id,
            type=serializer.validated_data["type"],
        )

        return serializer

    # ---------- /api/blog/comments/{id}/reactions/ ----------

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="reactions",
        permission_classes=[permissions.IsAuthenticated]
    )
    def reactions(self, request, pk=None):
        """
        - GET  /api/blog/comments/{comment_id}/reactions/
        - POST /api/blog/comments/{comment_id}/reactions/
        """
        comment = self.get_object()

        if request.method == "GET":
            serializer = self._get_comment_reactions(comment, request)
            return Response(serializer.data)

        # POST
        serializer = self._create_comment_reaction(comment, request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReactionViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Only update & delete reaction:
      - PATCH /api/blog/reactions/{id}/   -> update reaction type
      - DELETE /api/blog/reactions/{id}/  -> delete reaction
    """
    queryset = Reaction.objects.select_related("author", "content_type")
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ["patch", "delete", "head", "options"]
