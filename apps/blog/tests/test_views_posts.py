from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from .factories import (
    UserFactory,
    PostFactory,
    CommentFactory,
    ReactionFactory,
)


class PostAPITests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.post = PostFactory(author=self.user)


    def _post_list_url(self):
        return reverse("post-list")

    def _post_detail_url(self, post_id=None):
        return reverse("post-detail", kwargs={"pk": post_id or self.post.id})

    def _post_comments_url(self, post_id=None):
        return reverse("post-comments", kwargs={"pk": post_id or self.post.id})

    def _post_reactions_url(self, post_id=None):
        return reverse("post-reactions", kwargs={"pk": post_id or self.post.id})


    def test_list_posts(self):
        PostFactory()  # another post

        resp = self.client.get(self._post_list_url())

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)
        self.assertGreaterEqual(len(resp.data["results"]), 1)
        self.assertIn("title", resp.data["results"][0])

    def test_retrieve_post(self):
        resp = self.client.get(self._post_detail_url())

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.post.id)
        self.assertEqual(resp.data["title"], self.post.title)

    def test_create_post(self):
        payload = {
            "title": "New post",
            "content": "Hello world",
        }

        resp = self.client.post(self._post_list_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["title"], "New post")
        self.assertEqual(resp.data["author"]["id"], self.user.id)

    def test_full_update_post(self):
        payload = {
            "title": "Updated title",
            "content": "Updated content",
        }

        resp = self.client.put(self._post_detail_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "Updated title")
        self.assertEqual(resp.data["content"], "Updated content")

    def test_partial_update_post(self):
        payload = {
            "title": "Partially updated title",
        }

        resp = self.client.patch(self._post_detail_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "Partially updated title")

    def test_delete_post(self):
        url = self._post_detail_url()

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_post_comments(self):
        CommentFactory(post=self.post, author=self.user)
        CommentFactory(post=self.post)

        resp = self.client.get(self._post_comments_url())

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertIn("content", resp.data[0])

    def test_add_post_comment(self):
        payload = {
            "content": "Great post!",
        }

        resp = self.client.post(self._post_comments_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["content"], "Great post!")
        self.assertEqual(resp.data["author"]["id"], self.user.id)
        self.assertEqual(resp.data["post"], self.post.id)


    def test_get_post_reactions(self):
        ReactionFactory.for_post(post=self.post, author=self.user, type="like")

        resp = self.client.get(self._post_reactions_url())

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertIn("type", resp.data[0])

    def test_add_post_reaction(self):
        payload = {
            "type": "like",
        }

        resp = self.client.post(self._post_reactions_url(), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["type"], "like")
        self.assertEqual(resp.data["author"]["id"], self.user.id)
