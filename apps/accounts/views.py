from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from .serializers import LoginSerializer


# Create your views here.
User = get_user_model()


class LoginAPIView(APIView):
    @extend_schema(
        request=LoginSerializer,
        auth=[],
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "User account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "organization": (
                        user.organization.name if user.organization else None
                    ),
                    "branches": list(user.branches.values("id", "name")),
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff,
                },
            }
        )
