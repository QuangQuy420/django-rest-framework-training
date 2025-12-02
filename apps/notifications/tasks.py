from celery import shared_task
from django.core.mail import send_mail
from apps.blog.models import Comment, Post
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_new_comment_email(author_id, parent_comment_author_id, comment_id):
    post_author = User.objects.get(id=author_id)
    parent_comment_author = User.objects.get(id=parent_comment_author_id) if parent_comment_author_id else None
    comment = Comment.objects.select_related("post").get(id=comment_id)
    post = comment.post

    subject = f"New comment on your post: {post.title}"
    message = f"{comment.author.username} commented:\n\n{comment.content}"

    send_mail(
        subject,
        message,
        "no-reply@yourapp.com",
        [post_author.email],
        fail_silently=False,
    )

    if parent_comment_author:
        subject = f"New reply to your comment on: {post.title}"
        message = f"{comment.author.username} replied to your comment:\n\n{comment.content}"

        send_mail(
            subject,
            message,
            "no-reply@yourapp.com",
            [parent_comment_author.email],
            fail_silently=False,
        )

@shared_task
def send_new_reaction_email(recipient_user_id, reaction_type, content_type, object_id):
    recipient = User.objects.get(id=recipient_user_id)

    if content_type == "post":
        post = Post.objects.get(id=object_id)
        subject = f"New reaction on your post: {post.title}"
        message = f"Your post received a new {reaction_type} reaction."
    else:
        comment = Comment.objects.select_related("post").get(id=object_id)
        post = comment.post
        subject = f"New reaction on your comment on: {post.title}"
        message = f"Your comment received a new {reaction_type} reaction."

    send_mail(
        subject,
        message,
        "no-reply@yourapp.com",
        [recipient.email],
        fail_silently=False,
    )
