import unicodedata
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP

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
        return (
            obj.category.discount_percent
            if obj.category and obj.category.is_active
            else None
        )

    @extend_schema_field(serializers.CharField())
    def get_credit_used(self, obj):
        return format(
            Decimal(obj.credit_used()).quantize(
                Decimal("0.000"), rounding=ROUND_HALF_UP
            ),
            ".3f",
        )

    @extend_schema_field(serializers.CharField())
    def get_credit_remaining(self, obj):
        return format(
            Decimal(obj.credit_remaining()).quantize(
                Decimal("0.000"), rounding=ROUND_HALF_UP
            ),
            ".3f",
        )

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )

        if "branches" in data:
            branches = data["branches"]
        elif self.instance:
            branches = list(self.instance.branches.all())
        else:
            branches = []

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

        country_code = data.get(
            "country_code",
            getattr(self.instance, "country_code", None),
        )
        mobile_number = data.get(
            "mobile_number",
            getattr(self.instance, "mobile_number", None),
        )

        self.validate_customer_mobile_unique(
            country_code=country_code,
            mobile_number=mobile_number,
            organization=organization,
            branches=branches,
        )

        return data
    
    def validate_customer_mobile_unique(
        self,
        country_code,
        mobile_number,
        organization,
        branches,
    ):
        if not mobile_number or not country_code:
            return

        customers = Customer.objects.filter(
            country_code=country_code,
            mobile_number=mobile_number,
        )

        if self.instance:
            customers = customers.exclude(pk=self.instance.pk)

        # Organization-level uniqueness
        if (
            organization
            and customers.filter(organization=organization).exists()
        ):
            raise serializers.ValidationError({
                "mobile_number": (
                    "A customer with this country code and mobile number "
                    "already exists in this organization."
                )
            })

        # Branch-level uniqueness
        branch_ids = [branch.pk for branch in (branches or [])]

        if (
            branch_ids
            and customers.filter(branches__in=branch_ids).exists()
        ):
            raise serializers.ValidationError({
                "mobile_number": (
                    "A customer with this country code and mobile number "
                    "already exists in one of the selected branches."
                )
            })     
    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        self.validate_customer_mobile_unique(
            country_code=validated_data.get("country_code"),
            mobile_number=validated_data.get("mobile_number"),
            organization=validated_data.get("organization"),
            branches=validated_data.get("branches", []),
        )

        request = self.context["request"]
        user = request.user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        if {
            "country_code",
            "mobile_number",
            "organization",
            "branches",
        } & validated_data.keys():
            self.validate_customer_mobile_unique(
                country_code=validated_data.get(
                    "country_code", instance.country_code
                ),
                mobile_number=validated_data.get(
                    "mobile_number", instance.mobile_number
                ),
                organization=validated_data.get(
                    "organization", instance.organization
                ),
                branches=validated_data.get(
                    "branches", list(instance.branches.all())
                ),
            )

        request = self.context["request"]
        user = request.user
        instance.updated_by = user
        return super().update(instance, validated_data)
