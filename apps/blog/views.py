import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.blog.permissions import IsAuthorOrReadOnly
from apps.notifications.tasks import send_new_comment_email, send_new_reaction_email

from .models import Comment, Post, Reaction
from .serializers import CommentSerializer, PostSerializer, ReactionSerializer

logger = logging.getLogger(__name__)


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
        return Post.objects.select_related("author").prefetch_related(
            "reactions",
            "comments__author",
            "comments__reactions",
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # helper methods for comments on this post
    def _get_post_comments(self, post, request):
        comments = (
            post.comments.filter(parent__isnull=True)
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
        comment = serializer.save(author=request.user)

        # Get parent comment author id if this is a reply
        parent_id = data.get("parent") or request.data.get("parent")
        parent_author_id = None
        if parent_id:
            try:
                parent_comment = Comment.objects.select_related("author").get(id=parent_id)
                parent_author_id = parent_comment.author.id
            except Comment.DoesNotExist:
                parent_author_id = None

        try:
            send_new_comment_email.delay(post.author.id, parent_author_id, comment.id)
        except Exception as e:
            logger.error("Failed to enqueue reaction email task: %s", e)

        return serializer

    @action(detail=True, methods=["get", "post"], url_path="comments", permission_classes=[permissions.IsAuthenticated])
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
        reactions = Reaction.objects.filter(content_type=ct, object_id=post.id).select_related("author")
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

        new_type = serializer.validated_data["type"]
        ct = ContentType.objects.get_for_model(Post)

        # 1) Check existing reaction first (to compare types later)
        existing = Reaction.objects.filter(
            author=request.user,
            content_type=ct,
            object_id=post.id,
        ).first()
        old_type = existing.type if existing else None

        # 2) Upsert reaction
        with transaction.atomic():
            reaction, created = Reaction.objects.update_or_create(
                author=request.user,
                content_type=ct,
                object_id=post.id,
                defaults={"type": new_type},
            )

        # 3) Only send email if:
        #    - reaction is newly created, OR
        #    - the type actually changed
        if created or old_type != reaction.type:
            try:
                send_new_reaction_email.delay(
                    post.author.id,
                    reaction.type,
                    "post",
                    post.id,
                )
            except Exception as e:
                logger.error("Failed to enqueue reaction email task: %s", e)

        return ReactionSerializer(
            reaction,
            context={"request": request},
        )

    @action(
        detail=True, methods=["get", "post"], url_path="reactions", permission_classes=[permissions.IsAuthenticated]
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
        reactions = Reaction.objects.filter(content_type=ct, object_id=comment.id).select_related("author")
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

        new_type = serializer.validated_data["type"]
        ct = ContentType.objects.get_for_model(Comment)

        # 1) Check existing reaction first to compare types later
        existing = Reaction.objects.filter(
            author=request.user,
            content_type=ct,
            object_id=comment.id,
        ).first()

        old_type = existing.type if existing else None

        # 2) Upsert reaction
        with transaction.atomic():
            reaction, created = Reaction.objects.update_or_create(
                author=request.user,
                content_type=ct,
                object_id=comment.id,
                defaults={"type": new_type},
            )

        # 3) Only send email if:
        #    - reaction is newly created, OR
        #    - the type actually changed
        if created or old_type != reaction.type:
            try:
                send_new_reaction_email.delay(
                    comment.author.id,
                    reaction.type,
                    "comment",
                    comment.id,
                )
            except Exception as e:
                logger.error("Failed to enqueue reaction email task: %s", e)

        return ReactionSerializer(
            reaction,
            context={"request": request},
        )

    # ---------- /api/blog/comments/{id}/reactions/ ----------

    @action(
        detail=True, methods=["get", "post"], url_path="reactions", permission_classes=[permissions.IsAuthenticated]
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
