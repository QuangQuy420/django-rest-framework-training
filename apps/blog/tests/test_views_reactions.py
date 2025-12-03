from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.blog.models import Reaction

from .factories import CommentFactory, PostFactory, ReactionFactory, UserFactory


class PostReactionAPITests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.post = PostFactory()
        self.comment = CommentFactory(post=self.post)

    @patch("apps.notifications.tasks.send_new_reaction_email.delay")
    def test_create_reaction_first_time_sends_email(self, mock_delay):
        url = reverse("post-reactions", kwargs={"pk": self.post.id})
        payload = {"type": "like"}

        resp = self.client.post(url, payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reaction.objects.count(), 1)
        mock_delay.assert_called_once()  # email enqueued

    @patch("apps.notifications.tasks.send_new_reaction_email.delay")
    def test_same_type_reaction_does_not_resend_email(self, mock_delay):
        url = reverse("post-reactions", kwargs={"pk": self.post.id})

        # First time → should send email
        resp1 = self.client.post(url, {"type": "like"}, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reaction.objects.count(), 1)
        mock_delay.assert_called_once()

        # Reset mock to only track second call
        mock_delay.reset_mock()

        # Second time same type → should NOT send email
        resp2 = self.client.post(url, {"type": "like"}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reaction.objects.count(), 1)
        mock_delay.assert_not_called()  # no new email

    def test_update_reaction_type(self):
        url = reverse("post-reactions", kwargs={"pk": self.post.id})

        # Create initial reaction
        resp1 = self.client.post(url, {"type": "like"}, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Update reaction type
        resp2 = self.client.post(url, {"type": "love"}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Reaction.objects.count(), 1)
        reaction = Reaction.objects.get()
        self.assertEqual(reaction.type, "love")

    def test_delete_reaction(self):
        # Create a reaction via factory
        reaction = ReactionFactory.for_post(post=self.post, author=self.user, type="like")
        self.assertEqual(Reaction.objects.count(), 1)

        delete_url = reverse("reaction-detail", kwargs={"pk": reaction.id})
        resp = self.client.delete(delete_url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reaction.objects.count(), 0)
