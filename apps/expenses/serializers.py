from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.organizations.mixins import OrgBranchAssignMixin
from .models import ExpenseCategory, Expense


class ExpenseCategorySerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseCategory
        fields = [
            "id", "name", "name_ar", "is_active",
            "organization", "organization_name",
            "branches", "branch_names",
            "created_by", "created_by_name",
            "updated_by", "updated_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(serializers.ListSerializer(child=serializers.CharField()))
    def get_branch_names(self, obj):
        return [b.name for b in obj.branches.all()]


class ExpenseSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id", "expense_no", "category", "category_name",
            "amount", "expense_date", "description",
            "payment_mode", "reference_no", "is_active",
            "organization", "organization_name",
            "branches", "branch_names",
            "created_by", "created_by_name",
            "updated_by", "updated_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "expense_no", "created_at", "updated_at", "created_by", "updated_by"]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(serializers.ListSerializer(child=serializers.CharField()))
    def get_branch_names(self, obj):
        return [b.name for b in obj.branches.all()]

    @extend_schema_field(serializers.CharField())
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
