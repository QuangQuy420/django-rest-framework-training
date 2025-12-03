from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Comment, Post, Reaction


class ReactionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ["id", "type", "created_at", "author"]


class CommentReplySerializer(serializers.ModelSerializer):
    """
    Used for replies only (1 level deep).
    No `replies` field here → avoids deep recursion.
    """

    author = UserSerializer(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "created_at",
            "author",
            "reactions",
            "parent",
            "post",
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "created_at",
            "author",
            "reactions",
            "replies",
            "parent",
            "post",
        ]

    def validate(self, attrs):
        """
        Ensure parent comment (if any) belongs to the same post.
        """
        post = attrs.get("post") or self.context.get("post")
        parent = attrs.get("parent")

        if parent and parent.post_id != post.id:
            raise serializers.ValidationError({"parent": "Parent comment must belong to the same post."})
        return attrs

    def get_replies(self, obj):
        """
        Recursively return child comments until max_depth is reached.
        """
        depth = self.context.get("depth", 0)
        max_depth = self.context.get("max_depth", 5)

        if depth >= max_depth:
            return []

        # Get direct children
        queryset = (
            obj.replies.all()
            .select_related("author")
            .prefetch_related(
                "reactions",
                "replies__author",
                "replies__reactions",
            )
        )

        serializer = CommentSerializer(
            queryset,
            many=True,
            context={**self.context, "depth": depth + 1},
        )
        return serializer.data


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "author",
            "reactions",
            "comments",
        ]
