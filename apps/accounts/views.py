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
    RequestPasswordResetByUsernameSerializer,
    OTPPasswordResetSerializer,
    ForgotUsernameSerializer,
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
        vat_registration_number = None
        org_name = None
        is_org_user = False

        if org:
            # Case 1: user has root organization
            currency_code = org.currency_code
            vat_percent = org.service_vat_percent
            vat_registration_number = org.vat_registration_number
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
                vat_registration_number = branch.vat_registration_number or (
                    branch.parent.vat_registration_number if branch.parent else None
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
                    "organization_vat_registration_number": vat_registration_number,
                    "branches": list(user.branches.values("id", "name")),
                    "is_org_user": is_org_user,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff,
                },
            }
        )


class SuperAdminLoginAPIView(APIView):
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

        if not user.is_superuser:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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
        vat_registration_number = None
        org_name = None
        is_org_user = False

        if org:
            # Case 1: user has root organization
            currency_code = org.currency_code
            vat_percent = org.service_vat_percent
            vat_registration_number = org.vat_registration_number
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
                vat_registration_number = branch.vat_registration_number or (
                     branch.parent.vat_registration_number if branch.parent else None
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
                    "organization_vat_registration_number": vat_registration_number,
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
            vat_registration_number = org.vat_registration_number
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
                vat_percent = branch.vat_registration_number or (
                    branch.parent.vat_registration_number if branch.parent else None
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
                "organization_vat_registration_number": vat_registration_number,
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
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Request OTP (username -> send OTP to that user's email)
@extend_schema(
    tags=["Password Reset"],
    summary="Request OTP for password reset (by username)",
    description="User provides username. OTP will be sent to the email associated with that username (if exists).",
)
class RequestPasswordResetOTPView(APIView):
    serializer_class = RequestPasswordResetByUsernameSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Dont reveal whether user exists
            return Response(
                {
                    "detail": "If the username exists, an OTP has been sent to the associated email."
                },
                status=200,
            )

        # clear previous unused OTPs
        PasswordResetOTP.objects.filter(user=user, is_used=False).delete()

        # generate and save new OTP
        otp = PasswordResetOTP.generate_otp()

        PasswordResetOTP.objects.create(user=user, otp_code=otp)

        # send email with OTP
        subject = "Your Password Reset OTP"
        html_message = render_to_string(
            "emails/otp_password_reset.html",
            {
                "username": user.username,
                "otp": otp,
                "expiry_minutes": 10,
            },
        )

        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(
                subject,
                plain_message,
                from_email,
                [user.email],
                html_message=html_message,
            )
        except Exception as e:
            return Response({"detail": f"Email send failed: {str(e)}"}, status=500)

        return Response(
            {"detail": "OTP sent to the email linked with this username."}, status=200
        )


# Reset password using username + otp + new passwords (single API)
@extend_schema(
    tags=["Password Reset"],
    summary="Verify OTP and reset password (username + otp + new password)",
    description="Provide username, OTP (sent to user's email) and new password + confirm password in one request.",
)
class ResetPasswordWithOTPView(APIView):
    serializer_class = OTPPasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password reset successfully."}, status=200)


# Forgot username (send HTML email listing usernames tied to the email)
@extend_schema(
    tags=["Password Reset"],
    summary="Forgot username - send usernames linked to an email",
    description="User provides email. All usernames associated with that email will be sent to the email address (HTML).",
)
class ForgotUsernameView(APIView):
    serializer_class = ForgotUsernameSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        users = User.objects.filter(email=email)

        # Compose HTML email
        if users.exists():
            usernames = [u.username for u in users]
            html_message = render_to_string(
                "emails/forgot_username.html", {"usernames": usernames}
            )

            plain_message = strip_tags(html_message)
            subject = "Usernames linked to your email"
            from_email = settings.DEFAULT_FROM_EMAIL
            try:
                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [email],
                    html_message=html_message,
                )
            except Exception as e:
                return Response({"detail": f"Email send failed: {str(e)}"}, status=500)

        return Response(
            {
                "detail": "If any accounts are linked to this email, their username(s) have been sent."
            },
            status=200,
        )


# Change Password View for authenticated users using current password
@extend_schema(
    tags=["Password Reset"],
    summary="Change password using current password",
    description="Authenticated user enters current password + new password + confirm password.",
)
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )
