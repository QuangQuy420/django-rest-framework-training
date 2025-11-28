from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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


class CookieTokenRefreshView(TokenRefreshView):
    """
    POST /api/users/token/refresh/

    - Takes refresh token from HttpOnly cookie: "refresh_token"
    - Returns new access token in JSON: { "access": "..." }
    - Rotates refresh token and updates cookie
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "No refresh token cookie"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Use SimpleJWT serializer with the cookie value
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        access = data.get("access")
        new_refresh = data.get("refresh", None)  # only present if rotation enabled

        response_data = {"access": access}

        response = Response(response_data, status=status.HTTP_200_OK)
        if new_refresh:
            max_age = 7 * 24 * 60 * 60  # default 7 days

            response.set_cookie(
                "refresh_token",
                new_refresh,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=max_age,
            )

        return response


class LogoutView(APIView):
    """
    POST /api/users/logout/
    Authorization: Bearer <access_token>
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()      # Blacklist token (cannot be used again)
            except Exception:
                pass

        response = Response({"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie("refresh_token")

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
