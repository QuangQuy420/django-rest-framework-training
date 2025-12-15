from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import connections
from django.db.utils import OperationalError
from django.utils import timezone

from apps.blog.models import Comment, Post

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

    return "Comment emails sent."


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

    return "Reaction email sent."


@shared_task
def send_email_to_signed_up_user(user_id):
    user = User.objects.get(id=user_id)

    if not user or not user.email:
        return

    subject = "Welcome to Our Blog Platform!"
    message = (
        f"Hi {user.username},\n\nThank you for signing up for our blog platform. We're excited to have you on board!"
    )

    send_mail(
        subject,
        message,
        "no-reply@yourapp.com",
        [user.email],
        fail_silently=False,
    )

    return "Welcome email sent."


@shared_task
def check_db_health():
    """
    Tries to connect to the DB. If it fails, sends an email.
    """
    try:
        conn = connections["default"]
        conn.cursor()
    except OperationalError:
        send_mail(
            subject="[CRITICAL] Database Health Check Failed",
            message="The main database is not reachable. Please check immediately.",
            from_email="no-reply@yourapp.com",
            recipient_list=["quypq.dev@gmail.com"],
            fail_silently=False,
        )
        return "DB Check Failed - Email Sent"

    return "DB Check Passed"


@shared_task
def send_daily_signup_report():
    """
    Filters users who joined 'today' and sends a list to Admin.
    """
    User = get_user_model()
    today = timezone.now().date()

    # Get users who joined today (00:00 to 23:59)
    new_users = User.objects.filter(date_joined__date=today)

    if not new_users.exists():
        return "No new users today."

    user_list_text = "\n".join([f"- {u.username} ({u.email})" for u in new_users])
    message = f"Here is the list of users who signed up on {today}:\n\n{user_list_text}"

    send_mail(
        subject=f"Daily Signup Report - {today}",
        message=message,
        from_email="no-reply@yourapp.com",
        recipient_list=["quypq.dev@gmail.com"],
        fail_silently=False,
    )

    return f"Report sent for {new_users.count()} users."
