from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from random import randint

# package imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry mixin imports
from apps.accounts.mixins import GroupOrgBranchQuerysetMixin
from apps.organizations.mixins import OrgBranchQuerysetMixin

# laundry permission validator
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

# laundry model imports
from .models import AuthUser, PasswordResetOTP

# laundry serializer imports
from .serializers import (
    AuthUserSerializer,
    PermissionSerializer,
    GroupSerializer,
    LoginSerializer,
    UserTokenSerializer,
    RequestPasswordResetOTPSerializer,
    OTPPasswordResetSerializer,
    ChangePasswordSerializer,
)


# Create your views here.
User = get_user_model()


@extend_schema(tags=["Users"])
class UserListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [MultiPartParser, FormParser]

    permission_map = {
        "GET": "accounts.view_authuser",
        "POST": "accounts.add_authuser",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("id")


@extend_schema(tags=["Users"])
class UserRetrieveUpdateDestroyView(
    PermissionRequiredMixin,
    OrgBranchQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [MultiPartParser, FormParser]

    permission_map = {
        "GET": "accounts.view_authuser",
        "PUT": "accounts.change_authuser",
        "PATCH": "accounts.change_authuser",
        "DELETE": "accounts.delete_authuser",
    }


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
class GroupListCreateView(
    PermissionRequiredMixin, GroupOrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [JSONParser]

    permission_map = {
        "GET": "auth.view_group",  # list groups
        "POST": "auth.add_group",  # create group
    }

    def get_queryset(self):
        return super().get_queryset().order_by("name")


@extend_schema(tags=["Groups"])
class GroupRetrieveUpdateDestroyView(
    PermissionRequiredMixin,
    GroupOrgBranchQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [JSONParser]

    permission_map = {
        "GET": "auth.view_group",
        "PUT": "auth.change_group",
        "PATCH": "auth.change_group",
        "DELETE": "auth.delete_group",
    }


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

        org = user.organization
        currency_code = None
        vat_percent = None
        org_name = None
        is_org_user = False

        if org:
            # Case 1: user has root organization
            currency_code = org.currency_code
            vat_percent = org.service_vat_percent
            org_name = org.name
            is_org_user = True

        elif user.branches.exists():
            # Case 2: user has branches
            branch = user.branches.first()
            if branch:
                org_name = branch.name  # branch name
                # Prefer branch values if available
                currency_code = branch.currency_code or (
                    branch.parent.currency_code if branch.parent else None
                )
                vat_percent = branch.service_vat_percent or (
                    branch.parent.service_vat_percent if branch.parent else None
                )
                # If parent exists, prefer parent name as organization name
                if branch.parent:
                    org_name = branch.parent.name

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "profile_picture": (
                        request.build_absolute_uri(user.profile_picture.url)
                        if user.profile_picture
                        else None
                    ),
                    "email": user.email,
                    "groups": list(user.groups.values_list("id", flat=True)),
                    "organization_name": org_name,
                    "organization_currency_code": currency_code,
                    "organization_service_vat_percent": vat_percent,
                    "branches": list(user.branches.values("id", "name")),
                    "is_org_user": is_org_user,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff,
                },
            }
        )


class UserTokenDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserTokenSerializer

    def get(self, request):
        user = request.user
        org = user.organization
        currency_code = None
        vat_percent = None
        org_name = None
        is_org_user = False

        if org:
            # Case 1: user has root organization
            currency_code = org.currency_code
            vat_percent = org.service_vat_percent
            org_name = org.name
            is_org_user = True

        elif user.branches.exists():
            # Case 2: user has branches
            branch = user.branches.first()
            if branch:
                org_name = branch.name  # branch name
                # Prefer branch values if available
                currency_code = branch.currency_code or (
                    branch.parent.currency_code if branch.parent else None
                )
                vat_percent = branch.service_vat_percent or (
                    branch.parent.service_vat_percent if branch.parent else None
                )
                # If parent exists, prefer parent name as organization name
                if branch.parent:
                    org_name = branch.parent.name

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "profile_picture": (
                    request.build_absolute_uri(user.profile_picture.url)
                    if user.profile_picture
                    else None
                ),
                "email": user.email,
                "groups": list(user.groups.values_list("id", flat=True)),
                "organization_name": org_name,
                "organization_currency_code": currency_code,
                "organization_service_vat_percent": vat_percent,
                "branches": list(user.branches.values("id", "name")),
                "is_org_user": is_org_user,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PASSWORD RESET VIA OTP
# ============================================================

@extend_schema(
    tags=["Password Reset"],
    summary="Request OTP for password reset",
    description=(
        "User enters email. If the email exists, a new OTP is sent. "
        "Even if the email does not exist, same response is returned for security."
    ),
)
class RequestPasswordResetOTPView(APIView):
    """
    Step 1: User enters their email to get OTP.
    """
    serializer_class = RequestPasswordResetOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Avoid leaking existence of user
            return Response({"detail": "If your email exists, OTP has been sent."}, status=200)

        # Delete any existing unused OTPs for this user
        PasswordResetOTP.objects.filter(user=user, is_used=False).delete()

        # Generate a 6-digit OTP
        otp = PasswordResetOTP.generate_otp()

        # Save OTP to DB
        PasswordResetOTP.objects.create(user=user, otp_code=otp)

        # Send OTP to email
        subject = "Your Password Reset OTP"
        message = f"Hello {user.username},\n\nYour OTP for password reset is: {otp}\nIt will expire in 10 minutes.\n\nThanks,\nLaundry Team"
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [email])
        except Exception as e:
            return Response({"detail": f"Email send failed: {str(e)}"}, status=500)

        return Response({"detail": "OTP sent to your email successfully."}, status=200)
    

# OTP Verification View
@extend_schema(
    tags=["Password Reset"],
    summary="Verify OTP and reset password",
    description="User provides email, OTP, new password, and confirm password. If OTP is valid, password is reset.",
)
class ResetPasswordWithOTPView(APIView):
    serializer_class = OTPPasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password reset successfully."}, status=200)


# Change Password View for authenticated users using current password
@extend_schema(
    tags=["Password Reset"],
    summary="Change password using current password",
    description="Authenticated user enters current password + new password + confirm password.",
)
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ['patch'] 

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)