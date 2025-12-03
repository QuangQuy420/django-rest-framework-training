from django.contrib import admin

from .models import Comment, Post, Reaction


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at", "updated_at")
    search_fields = ("title", "content", "author__username")
    list_filter = ("created_at", "author")
    ordering = ("-created_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "parent", "created_at")
    search_fields = ("content", "author__username", "post__title")
    list_filter = ("created_at", "author")

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "type", "content_type", "created_at")
    search_fields = ("user__username", "content_type")
    list_filter = ("content_type", "created_at", "author")
