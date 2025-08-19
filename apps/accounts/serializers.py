from django.db.models import Q
from django.contrib.auth.models import Permission, Group

# package imports
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# laundry model imports
from .models import AuthUser, GroupDetail


from django.contrib.auth.models import Group


class AuthUserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    branch_names = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )

    class Meta:
        model = AuthUser
        fields = [
            "id",
            "username",
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


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]


class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupDetail
        fields = [
            "description",
            "organization",
            "branches",
        ]


class GroupSerializer(serializers.ModelSerializer):
    detail = GroupDetailSerializer(required=False)
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ["id", "name", "detail", "permissions"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        filtered_permissions = instance.permissions.filter(
            Q(detail__isnull=True) | Q(detail__is_staff_only=False)
        ).values_list("id", flat=True)

        representation["permissions"] = list(filtered_permissions)
        return representation

    def create(self, validated_data):
        detail_data = validated_data.pop("detail", None)
        permissions_data = validated_data.pop("permissions", [])

        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions_data)

        if detail_data:
            detail_instance, _ = GroupDetail.objects.get_or_create(group=group)
            for attr, value in detail_data.items():
                setattr(detail_instance, attr, value)
            detail_instance.save()

        group.refresh_from_db()
        return group

    def update(self, instance, validated_data):
        detail_data = validated_data.pop("detail", None)
        permissions_data = validated_data.pop("permissions", None)

        instance.name = validated_data.get("name", instance.name)
        instance.save()

        if permissions_data is not None:
            instance.permissions.set(permissions_data)

        if detail_data:
            detail_instance, _ = GroupDetail.objects.get_or_create(group=instance)
            for attr, value in detail_data.items():
                setattr(detail_instance, attr, value)
            detail_instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserTokenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    organization_name = serializers.CharField(allow_null=True)
    organization_currency_code = serializers.CharField(allow_null=True)
    organization_service_vat_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True
    )
    branches = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()
