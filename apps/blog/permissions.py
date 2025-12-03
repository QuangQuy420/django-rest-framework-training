from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    - SAFE methods (GET, HEAD, OPTIONS) -> allowed for all authenticated users
    - Other methods (PUT, PATCH, DELETE) -> only allowed for the author of the post
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the author can update/delete
        print("obj", obj.author)
        print("request", request.user)
        return obj.author == request.user
