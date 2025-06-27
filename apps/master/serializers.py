# package imports
from rest_framework import serializers

# master model imports
from .models import ClothType, WashingType


# serializers.py
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

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches", getattr(self.instance, "branches", None))

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


class WashingTypeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = WashingType
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches", getattr(self.instance, "branches", None))

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
