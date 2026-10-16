from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.hashers import make_password

# package imports
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_field

# laundry mixin imports
from .mixins import GroupOrgBranchAssignMixin
from apps.organizations.mixins import OrgBranchAssignMixin

# laundry model imports
from .models import AuthUser, GroupDetail, PasswordResetOTP
from apps.organizations.models import OrganizationSubscription


User = get_user_model()


class AuthUserSerializer(serializers.ModelSerializer, OrgBranchAssignMixin):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    branch_names = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )

    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = AuthUser
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "address",
            "country_code",
            "mobile_number",
            "profile_picture",
            "groups",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
        ]
        extra_kwargs = {
            "organization": {"required": False, "allow_null": True},
            "branches": {"required": False},
            "groups": {"required": False},
        }

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [b.name for b in obj.branches.all()]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        organization = validated_data.get("organization")
        branches = validated_data.get("branches")

        # User must belong to either an organization or at least one branch
        if not organization and not branches:
            raise ValidationError(
                "Either an organization or at least one branch is required."
            )

        # Determine the root organization for subscription/plan checks
        if organization:
            root_org = organization.parent if organization.parent else organization
        else:
            # If only branches are assigned, get the root organization
            branch = branches[0]
            root_org = branch.parent

        subscription = (
            OrganizationSubscription.objects.filter(
                organization=root_org,
                started_at__lte=timezone.now(),
                expires_at__gte=timezone.now(),
            )
            .order_by("-id")
            .first()
        )

        if not subscription:
            raise ValidationError("No active subscription found.")

        max_users = subscription.plan.max_users

        org_ids = list(root_org.branches.values_list("id", flat=True))
        org_ids.append(root_org.id)

        current_users = AuthUser.objects.filter(organization_id__in=org_ids).count()

        if current_users >= max_users:
            raise ValidationError(
                f"User limit reached ({max_users}). Upgrade your plan."
            )

        request = self.context["request"]
        user = request.user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        password = validated_data.pop("password", None)
        instance = super().create(validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)
        request = self.context["request"]
        user = request.user
        instance.updated_by = user

        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]


class GroupDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = GroupDetail
        fields = [
            "description",
            "organization",
            "branches",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
        ]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None


class GroupSerializer(serializers.ModelSerializer, GroupOrgBranchAssignMixin):
    detail = GroupDetailSerializer(required=False)
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ["id", "name", "detail", "permissions"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        name = representation["name"]
        if "_" in name:
            base, suffix = name.rsplit("_", 1)
            if suffix.isdigit() and len(suffix) >= 14:
                representation["name"] = base

        filtered_permissions = instance.permissions.filter(
            Q(detail__isnull=True) | Q(detail__is_staff_only=False)
        ).values_list("id", flat=True)

        representation["permissions"] = list(filtered_permissions)
        return representation

    def create(self, validated_data):
        detail_data = validated_data.pop("detail", None)
        permissions_data = validated_data.pop("permissions", [])

        base_name = validated_data.get("name").strip()

        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        validated_data["name"] = f"{base_name}_{timestamp}"
        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions_data)

        self.assign_org_branch_on_create(group, {"detail": detail_data or {}})

        group.refresh_from_db()
        return group

    def update(self, instance, validated_data):
        detail_data = validated_data.pop("detail", None)
        permissions_data = validated_data.pop("permissions", None)

        if "name" in validated_data:
            base_name = validated_data["name"].strip()
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            instance.name = f"{base_name}_{timestamp}"

        instance.save()

        if permissions_data is not None:
            instance.permissions.set(permissions_data)

        self.assign_org_branch_on_update(instance, {"detail": detail_data or {}})

        instance.refresh_from_db()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserTokenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    email = serializers.EmailField()
    organization_name = serializers.CharField(allow_null=True)
    organization_currency_code = serializers.CharField(allow_null=True)
    organization_service_vat_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True
    )
    branches = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    is_org_user = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()

    class Meta:
        model = get_user_model()
        fields = "__all__"


# Password Reset Serializers using username
# =======================
class RequestPasswordResetByUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        # username is unique in AbstractUser by default, so .get is fine
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username does not exist.")
        return value


# Serializer for verifying OTP and resetting password
class OTPPasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        otp = attrs.get("otp")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                "New password and confirm password do not match."
            )

        # Validate OTP
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or OTP.")

        # Check if OTP exists and is valid
        otp_obj = PasswordResetOTP.objects.filter(user=user, otp_code=otp).last()

        if not otp_obj or not otp_obj.is_valid():
            raise serializers.ValidationError("OTP is invalid or expired.")

        attrs["user"] = user
        attrs["otp_obj"] = otp_obj
        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp_obj = self.validated_data["otp_obj"]
        new_password = self.validated_data["new_password"]

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        return user


class ForgotUsernameSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Do not reveal whether the email exists in the system
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                "New password and confirm password do not match."
            )
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
