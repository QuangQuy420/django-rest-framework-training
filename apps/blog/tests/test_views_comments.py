from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from .factories import UserFactory, PostFactory, CommentFactory


class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.post = PostFactory()


    def _post_comments_url(self, post_id=None):
        return reverse("post-comments", kwargs={"pk": post_id or self.post.id})

    def _comment_detail_url(self, comment_id):
        return reverse("comment-detail", kwargs={"pk": comment_id})


    def test_list_comments_of_post(self):
        CommentFactory(post=self.post)
        CommentFactory(post=self.post)

        resp = self.client.get(self._post_comments_url())

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertIn("content", resp.data[0])

    def test_create_top_level_comment(self):
        payload = {
            "content": "Nice post!",
            "parent": None,
        }

        resp = self.client.post(self._post_comments_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["content"], "Nice post!")
        self.assertEqual(resp.data["author"]["id"], self.user.id)
        self.assertEqual(resp.data["post"], self.post.id)
        self.assertIsNone(resp.data["parent"])

    def test_create_reply_comment(self):
        parent = CommentFactory(post=self.post)

        payload = {
            "content": "Reply here",
            "parent": parent.id,
        }

        resp = self.client.post(self._post_comments_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["parent"], parent.id)
        self.assertEqual(resp.data["post"], self.post.id)
        self.assertEqual(resp.data["author"]["id"], self.user.id)


    def test_update_comment(self):
        comment = CommentFactory(post=self.post, author=self.user)

        url = self._comment_detail_url(comment.id)
        payload = {
            "content": "Updated content",
        }

        resp = self.client.patch(url, payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["content"], "Updated content")

    def test_delete_comment(self):
        comment = CommentFactory(post=self.post, author=self.user)

        url = self._comment_detail_url(comment.id)
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
