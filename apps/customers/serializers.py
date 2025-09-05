# package imports
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# laundry mixin imports
from apps.organizations.mixins import OrgBranchAssignMixin

# laundry model imports
from .models import Customer, CustomerCategory


# customer category serializers
class CustomerCategorySerializer(serializers.ModelSerializer, OrgBranchAssignMixin):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = CustomerCategory
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
        instance = self.assign_org_branch_on_update(instance, validated_data)
        request = self.context["request"]
        user = request.user
        instance.updated_by = user
        return super().update(instance, validated_data)


# customer serializers
class CustomerSerializer(serializers.ModelSerializer, OrgBranchAssignMixin):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    category_discount = serializers.SerializerMethodField()
    credit_used = serializers.SerializerMethodField()
    credit_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = (
            "customer_id",
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

    @extend_schema_field(serializers.CharField())
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    @extend_schema_field(serializers.DecimalField(max_digits=5, decimal_places=2))
    def get_category_discount(self, obj):
        return obj.category.discount_percent if obj.category else None

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_credit_used(self, obj):
        return obj.credit_used()

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_credit_remaining(self, obj):
        return obj.credit_remaining()

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
        instance = self.assign_org_branch_on_update(instance, validated_data)
        request = self.context["request"]
        user = request.user
        instance.updated_by = user
        return super().update(instance, validated_data)
