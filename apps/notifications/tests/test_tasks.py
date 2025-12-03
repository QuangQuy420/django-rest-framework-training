from django.core import mail
from django.test import TestCase, override_settings

from apps.blog.tests.factories import CommentFactory, PostFactory, UserFactory
from apps.notifications.tasks import (
    send_new_comment_email,
    send_new_reaction_email,
)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class NotificationTaskTests(TestCase):
    def _assert_single_email(self, subject_contains, body_contains, to):
        """Helper: assert there's exactly one email with expected content."""
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(subject_contains, email.subject)
        self.assertIn(body_contains, email.body)
        self.assertEqual(email.to, [to])
        mail.outbox.clear()

    def test_send_new_comment_email_sends_mail(self):
        author = UserFactory()
        post = PostFactory(author=author)
        comment = CommentFactory(post=post)

        # parent_author_id=None because this is a top-level comment
        send_new_comment_email(author.id, None, comment.id)

        self._assert_single_email(
            subject_contains=post.title,
            body_contains=comment.content,
            to=author.email,
        )

    def test_send_new_comment_email_sends_reply_mail(self):
        author = UserFactory()
        parent_comment_author = UserFactory()
        post = PostFactory(author=author)
        parent_comment = CommentFactory(post=post, author=parent_comment_author)
        reply_comment = CommentFactory(
            post=post,
            author=UserFactory(),
            parent=parent_comment,
        )

        # Expect: email to post author AND to parent comment author
        send_new_comment_email(author.id, parent_comment_author.id, reply_comment.id)

        self.assertEqual(len(mail.outbox), 2)
        email_to_post_author = mail.outbox[0]
        email_to_parent_author = mail.outbox[1]

        # Email 1 → post author
        self.assertIn(post.title, email_to_post_author.subject)
        self.assertIn(reply_comment.content, email_to_post_author.body)
        self.assertEqual(email_to_post_author.to, [author.email])

        # Email 2 → parent comment author
        self.assertIn(post.title, email_to_parent_author.subject)
        self.assertIn(reply_comment.content, email_to_parent_author.body)
        self.assertEqual(email_to_parent_author.to, [parent_comment_author.email])

        mail.outbox.clear()

    def test_send_new_reaction_email_sends_mail_for_post(self):
        author = UserFactory()
        post = PostFactory(author=author)

        send_new_reaction_email(
            recipient_user_id=author.id,
            reaction_type="like",
            content_type="post",
            object_id=post.id,
        )

        self._assert_single_email(
            subject_contains=post.title,
            body_contains="like",
            to=author.email,
        )

    def test_send_new_reaction_email_sends_mail_for_comment(self):
        author = UserFactory()
        post = PostFactory(author=author)
        comment = CommentFactory(post=post)

        send_new_reaction_email(
            recipient_user_id=author.id,
            reaction_type="love",
            content_type="comment",
            object_id=comment.id,
        )

        self._assert_single_email(
            subject_contains=post.title,
            body_contains="love",
            to=author.email,
        )
