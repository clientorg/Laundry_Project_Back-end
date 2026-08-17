# package imports
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# laundry model imports
from .models import Branch

# subscription service imports
from apps.organizations.services.subscription_service import (
    check_branch_limit,
    BranchLimitExceeded,
    get_active_subscription,
)


class BranchSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "description",
            "currency_code",
            "service_vat_percent",
            "vat_registration_number",
            "address",
            "contact_name",
            "contact_mobile_number",
            "contact_email",
            "country",
            "country_code",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
        ]
        read_only_fields = ["id"]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        parent = None

        if user.organization:
            parent = user.organization
        elif user.branches.exists():
            branch = user.branches.first()
            parent = branch.parent

        if not parent:
            raise serializers.ValidationError(
                "Unable to determine parent organization from user."
            )
        
        # Check branch limit before creating a new branch
        try:
            check_branch_limit(parent)
        except BranchLimitExceeded as e:
            raise serializers.ValidationError({
                "detail": str(e)
            })  
           
        return Branch.objects.create(
            parent=parent,
            created_by=user,
            updated_by=user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        request = self.context["request"]
        user = request.user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = user
        instance.save()
        return instance


# -------------------------Organization Serializer
from .models import Organization
from .models import Plan

class OrganizationSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    active_plan = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "description",
            "address",
            "contact_name",
            "contact_mobile_number",
            "contact_email",
            "country",
            "country_code",
            "currency_code",
            "service_vat_percent",
            "vat_registration_number",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "active_plan",
        ]
        read_only_fields = ["id"]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def get_active_plan(self, obj):
        subscription = get_active_subscription(obj)

        if not subscription:
            return None

        plan = subscription.plan
        return {
            "id": plan.id,
            "name": plan.name,
            "price": plan.price,
            "max_users": plan.max_users,
            "max_branches": plan.max_branches,
            "started_at": subscription.started_at,
            "expires_at": subscription.expires_at,
        }
    
    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return Organization.objects.create(**validated_data)

        

    def update(self, instance, validated_data):
        request = self.context["request"]
        user = request.user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = user
        instance.save()
        return instance

# ------------------------- Plan Serializer
from .models import Plan

class PlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "description",
            "price",
            "max_branches",
            "duration_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# -------------------------Change Plan Serializer
class ChangePlanSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()


# ------------------------- Organization Subscription Serializer
from .models import OrganizationSubscription


class OrganizationSubscriptionSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationSubscription
        fields = [
            "id",
            "organization",
            "organization_name",
            "plan",
            "plan_name",
            "started_at",
            "expires_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "started_at",
            "expires_at",
            "is_active",
        ]

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    def get_plan_name(self, obj):
        return obj.plan.name if obj.plan else None

    def get_is_active(self, obj):
        return obj.is_active
    

# --------------------- INPUT VALIDATION SERIALIZERS --------------------- #
from django.contrib.auth import get_user_model

User = get_user_model()


# --------------------- USER INPUT VALIDATION --------------------- #
class UserInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value


# --------------------- PLAN INPUT VALIDATION --------------------- #
class PlanInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # max_users is optional as per Q1=B
    max_users = serializers.IntegerField(required=False, min_value=1)
    
    max_branches = serializers.IntegerField(min_value=1)
    duration_days = serializers.IntegerField(min_value=1)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value


# --------------------- ORGANIZATION INPUT VALIDATION --------------------- #
class OrganizationInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

    def validate_name(self, value):
        if Organization.objects.filter(name=value, parent__isnull=True).exists():
            raise serializers.ValidationError("Organization name already exists.")
        return value


# --------------------- WRAPPER SERIALIZER --------------------- #
class OrganizationSetupSerializer(serializers.Serializer):
    plan = PlanInputSerializer()
    organization = OrganizationInputSerializer()
    user = UserInputSerializer()
