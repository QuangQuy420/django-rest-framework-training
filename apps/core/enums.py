from django.db import models


class ReactionType(models.TextChoices):
    LIKE = "like", "Like"
    LOVE = "love", "Love"
    HAHA = "haha", "Haha"
    ANGRY = "angry", "Angry"
    SAD = "sad", "Sad"
    WOW = "wow", "Wow"
