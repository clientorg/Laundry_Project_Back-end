from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group

# package imports
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry serializer imports
from .serializers import PermissionSerializer, GroupSerializer, LoginSerializer


# Create your views here.
User = get_user_model()


@extend_schema(tags=["Permissions"])
class PermissionView(APIView):
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        permissions = (
            Permission.objects.all()
            .select_related("content_type")
            .filter(Q(detail__isnull=True) | Q(detail__is_staff_only=False))
        )
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Groups"])
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=["Groups"])
class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def perform_update(self, serializer):
        serializer.save()


@extend_schema(tags=["Groups"])
class GroupAssignedPermissionsView(APIView):
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, status=404)

        permissions_qs = group.permissions.select_related("content_type").filter(
            Q(detail__isnull=True) | Q(detail__is_staff_only=False)
        )
        serializer = PermissionSerializer(permissions_qs, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Groups"])
class GroupUnassignedPermissionsView(APIView):
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, status=404)

        assigned_ids = group.permissions.values_list("id", flat=True)
        unassigned_permissions = (
            Permission.objects.exclude(id__in=assigned_ids)
            .filter(Q(detail__isnull=True) | Q(detail__is_staff_only=False))
            .select_related("content_type")
        )

        serializer = PermissionSerializer(unassigned_permissions, many=True)
        return Response(serializer.data)


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

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
                    "organization_name": (
                        user.organization.name if user.organization else None
                    ),
                    "organization_currency_code": (
                        user.organization.currency_code if user.organization else None
                    ),
                    "organization_service_vat_percent": (
                        user.organization.service_vat_percent
                        if user.organization
                        else None
                    ),
                    "branches": list(user.branches.values("id", "name")),
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff,
                },
            }
        )


class UserTokenDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "organization_name": (
                    user.organization.name if user.organization else None
                ),
                "organization_currency_code": (
                    user.organization.currency_code if user.organization else None
                ),
                "organization_service_vat_percent": (
                    user.organization.service_vat_percent if user.organization else None
                ),
                "branches": list(user.branches.values("id", "name")),
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_200_OK,
        )
