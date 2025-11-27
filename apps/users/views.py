from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    {
      "username": "quy",
      "email": "quy@example.com",
      "password": "secret123"
    }
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/users/login/
    {
      "username": "...",
      "password": "..."
    }
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        refresh = data.get("refresh")
        if refresh:
            # Move refresh token to HttpOnly cookie (optional: remove from JSON)
            response.set_cookie(
                "refresh_token",
                refresh,
                httponly=True,
                secure=False,  # True in production with HTTPS
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,  # 7 days
            )
            del data["refresh"]  # don’t send in body

        response.data = data
        return response


class MeView(APIView):
    """
    GET /api/users/me/
    Authorization: Bearer <access_token>
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
