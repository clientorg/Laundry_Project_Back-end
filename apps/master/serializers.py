# package imports
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# laundry mixin imports
from apps.organizations.mixins import OrgBranchAssignMixin

# laundry model imports
from .models import Country, Item, ClothType, ServiceType, HandlingType, DeliveryType


# serializers.py
# country serializers
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer, OrgBranchAssignMixin):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                branch
                for branch in branches
                if not self.branch_belongs_to_org(branch, organization)
            ]
            if invalid_branches:
                branch_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do not belong to the organization '{organization.name}': {branch_names}"
                )
        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)
        request = self.context["request"]
        user = request.user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.assign_org_branch_on_update(validated_data)
        request = self.context["request"]
        user = request.user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)


# cloth type serializers
class ClothTypeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ClothType
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                branch
                for branch in branches
                if not self.branch_belongs_to_org(branch, organization)
            ]
            if invalid_branches:
                branch_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do not belong to the organization '{organization.name}': {branch_names}"
                )
        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization


# service type serializer
class ServiceTypeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ServiceType
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                branch
                for branch in branches
                if not self.branch_belongs_to_org(branch, organization)
            ]
            if invalid_branches:
                branch_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do not belong to the organization '{organization.name}': {branch_names}"
                )
        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization


# handling type serializer
class HandlingTypeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = HandlingType
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                branch
                for branch in branches
                if not self.branch_belongs_to_org(branch, organization)
            ]
            if invalid_branches:
                branch_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do not belong to the organization '{organization.name}': {branch_names}"
                )
        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization


# delivery type serializer
class DeliveryTypeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryType
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                branch
                for branch in branches
                if not self.branch_belongs_to_org(branch, organization)
            ]
            if invalid_branches:
                branch_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do not belong to the organization '{organization.name}': {branch_names}"
                )
        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization
