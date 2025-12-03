from django.test import TestCase
from apps.blog.models import Post, Comment
from apps.blog.serializers import CommentSerializer
from .factories import PostFactory, CommentFactory, UserFactory


class CommentSerializerTests(TestCase):
    def test_parent_must_belong_to_same_post(self):
        post_a = PostFactory()
        parent_comment = CommentFactory(post=post_a)

        post_b = PostFactory()

        data = {
            "content": "Reply on wrong post",
            "parent": parent_comment.id,
            "post": post_b.id,
        }

        serializer = CommentSerializer(data=data, context={"post": post_b})
        self.assertFalse(serializer.is_valid())
        self.assertIn("parent", serializer.errors)

    def test_nested_replies_structure(self):
        post = PostFactory()
        parent = CommentFactory(post=post)
        reply = CommentFactory(post=post, parent=parent)

        serializer = CommentSerializer(
            parent,
            context={"depth": 0, "max_depth": 5},
        )
        data = serializer.data

        self.assertEqual(data["id"], parent.id)
        self.assertEqual(len(data["replies"]), 1)
        self.assertEqual(data["replies"][0]["id"], reply.id)
