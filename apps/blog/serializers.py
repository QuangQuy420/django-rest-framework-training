from rest_framework import serializers
from .models import Post, Comment, Reaction
from apps.users.serializers import UserSerializer


class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ["id", "type", "created_at", "user"]


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
        ]

    def get_replies(self, obj):
        # Only 1 level of replies
        queryset = obj.replies.all()
        return CommentReplySerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


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
