import factory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.blog.models import Comment, Post, Reaction

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Post {n}")
    content = "Sample content"


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = "Comment content"
    parent = None


class ReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reaction

    author = factory.SubFactory(UserFactory)
    type = "like"

    @factory.lazy_attribute
    def content_type(self):
        # default: reaction on a Post
        return ContentType.objects.get_for_model(Post)

    @factory.lazy_attribute
    def object_id(self):
        # default: new Post if not overridden
        return PostFactory().id

    @classmethod
    def for_post(cls, post, **kwargs):
        """
        Convenience: create reaction for a specific Post
        """
        ct = ContentType.objects.get_for_model(Post)
        return cls(
            content_type=ct,
            object_id=post.id,
            **kwargs,
        )

    @classmethod
    def for_comment(cls, comment, **kwargs):
        """
        Convenience: create reaction for a specific Comment
        """
        ct = ContentType.objects.get_for_model(Comment)
        return cls(
            content_type=ct,
            object_id=comment.id,
            **kwargs,
        )
