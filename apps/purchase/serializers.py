from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.organizations.mixins import OrgBranchAssignMixin
#-------------------------- VAT Master Serializer --------------------------
from .models import VATMaster
class VATMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = VATMaster
        fields = [
            'id',
            "vatid",
            "vatname",
            "vatnamear",
            "vatper",
            "is_active",
            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ['id', "vatid","created_at","updated_at","created_by","updated_by",]
    
    # ---------- GETTERS ----------
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
        return [branch.name for branch in obj.branches.all()]

    # ---------- VALIDATION  ----------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid:
                names = ", ".join([b.name for b in invalid])
                raise serializers.ValidationError(
                    f"The following branches do not belong to organization '{organization.name}': {names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization  # Same condition as customer

    # ---------- CREATE ----------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    # ---------- UPDATE ----------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)
        user = self.context["request"].user
        instance.updated_by = user
        return super().update(instance, validated_data)

#----------------------- Supplier Master Serializer -----------------------
from .models import SupplierMaster
class SupplierMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = SupplierMaster
        fields = [
            "id",
            "name",
            "name_ar",
            "mobile",
            "email",
            "address",
            "country",
            "is_active",

            "organization",
            "organization_name",

            "branches",
            "branch_names",

            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


#----------------------- Group Master Serializer -----------------------
from .models import GroupMaster
class GroupMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = GroupMaster
        fields = [
            "id",
            "name",
            "name_ar",
            "is_active",

            "organization",
            "organization_name",

            "branches",
            "branch_names",

            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


#----------------------- Brand Master Serializer -----------------------
from .models import BrandMaster
class BrandMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = BrandMaster
        fields = [
            "id",
            "name",
            "name_ar",
            "is_active",

            "organization",
            "organization_name",

            "branches",
            "branch_names",

            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


#----------------------- ITGRP_MAP Serializer -----------------------
from .models import ITGRP_MAP
class ITGRP_MAPSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    grpname = serializers.SerializerMethodField()
    brdname = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ITGRP_MAP
        fields = [
            "id",
            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "grpcode",
            "grpname",
            "brdcode",
            "brdname",
            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    
    @extend_schema_field(serializers.CharField())
    def get_grpname(self, obj):
        return obj.grpcode.name if obj.grpcode else None

    @extend_schema_field(serializers.CharField())
    def get_brdname(self, obj):
        return obj.brdcode.name if obj.brdcode else None
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


#----------------------- Unit Master Serializer -----------------------
from .models import UnitMaster
class UnitMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = UnitMaster
        fields = [
            "id",
            "unitname",
            "unitnamear",
            "is_active",

            "organization",
            "organization_name",

            "branches",
            "branch_names",

            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",

            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


# ----------------------- Item Master Serializer -----------------------
from .models import ItemMaster

class ItemMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    unit_name = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    vat_name = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ItemMaster
        fields = [
            "id",

            "itname",
            "itnamear",

            "dubcost",
            "impcost",
            "itcost",

            "rtrate",
            "vatrate",

            "unit",
            "unit_name",

            "group_map",
            "group_name",
            "brand_name",

            "supplier",
            "supplier_name",

            "vat",
            "vat_name",

            "is_active",

            "organization",
            "organization_name",
            "branches",
            "branch_names",

            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_by", "updated_by", "created_at", "updated_at"]

    @extend_schema_field(serializers.CharField())
    def get_unit_name(self, obj):
        return obj.unit.unitname if obj.unit else None

    @extend_schema_field(serializers.CharField())
    def get_group_name(self, obj):
        if obj.group_map and obj.group_map.grpcode:
            return obj.group_map.grpcode.name
        return None

    @extend_schema_field(serializers.CharField())
    def get_brand_name(self, obj):
        if obj.group_map and obj.group_map.brdcode:
            return obj.group_map.brdcode.name
        return None

    @extend_schema_field(serializers.CharField())
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None

    @extend_schema_field(serializers.CharField())
    def get_vat_name(self, obj):
        return obj.vat.vatname if obj.vat else None

        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)
    

# ----------------------- Unit Map Serializer -----------------------
from .models import UnitMap

class UnitMapSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    alt_unit_name = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = UnitMap
        fields = [
            "id",
            "item",
            "item_name",
            "unit",
            "unit_name",
            "alt_unit",
            "alt_unit_name",
            "qty",
            "alt_qty",
            "is_active",
            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    
    @extend_schema_field(serializers.CharField())
    def get_item_name(self, obj):
        return obj.item.itname if obj.item else None

    @extend_schema_field(serializers.CharField())
    def get_unit_name(self, obj):
        return obj.unit.unitname if obj.unit else None

    @extend_schema_field(serializers.CharField())
    def get_alt_unit_name(self, obj):
        return obj.alt_unit.unitname if obj.alt_unit else None
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


# ----------------------- VR Type Master Serializer -----------------------
from .models import VRTypeMaster
class VRTypeMasterSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = VRTypeMaster
        fields = [
            "id",
            "vrname",
            "zipcode",
            "is_active",

            "organization",
            "organization_name",

            "branches",
            "branch_names",

            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",

            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "created_by", "updated_by", "updated_at")
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


# ----------------------- Inventory Transaction Serializer -----------------------
from .models import INV_TRAN

class INVTRANSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    item_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    vr_type_name = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    supplier_id = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = INV_TRAN
        fields = [
            "id",
            "item",
            "item_name",
            "unit",
            "unit_name",
            "vr_type",
            "vr_type_name",
            "qty",
            "rate",
            "amount",
            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "supplier_id",         
            "supplier_name",
            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    
    @extend_schema_field(serializers.CharField())
    def get_item_name(self, obj):
        return obj.item.itname if obj.item else None

    @extend_schema_field(serializers.CharField())
    def get_unit_name(self, obj):
        return obj.unit.unitname if obj.unit else None

    @extend_schema_field(serializers.CharField())
    def get_vr_type_name(self, obj):
        return obj.vr_type.vrname if obj.vr_type else None
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]
    
    @extend_schema_field(serializers.IntegerField())
    def get_supplier_id(self, obj):
        return obj.item.supplier.id if obj.item and obj.item.supplier else None

    @extend_schema_field(serializers.CharField())
    def get_supplier_name(self, obj):
        return obj.item.supplier.name if obj.item and obj.item.supplier else None

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


# ----------------------- Account Transaction Serializer -----------------------
from .models import ACC_TRAN

class ACCTRANSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    vr_type_name = serializers.SerializerMethodField()
    vat_name = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ACC_TRAN
        fields = [
            "id",
            "vrno",
            "serial_no",
            "voucher_date",

            "vr_type",
            "vr_type_name",

            "amount_ex_vat",
            "vat",
            "vat_name",
            "vat_amount",
            "amount_inc_vat",

            "reference_no",
            "reference_date",

            "paymode",
            "paid_to",
            "vatin",
            "narration",

            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "country",

            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [ "id", "vrno", "serial_no", "vat_amount", "amount_inc_vat", "created_by", "updated_by", "created_at", "updated_at"]
    
    @extend_schema_field(serializers.CharField())
    def get_vr_type_name(self, obj):
        return obj.vr_type.vrname if obj.vr_type else None

    @extend_schema_field(serializers.CharField())
    def get_vat_name(self, obj):
        return obj.vat.vatname if obj.vat else None

        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


# ----------------------- Account Master Serializer -----------------------
from .models import ACCT_MAST

class ACCTMASTSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ACCT_MAST
        fields = [
            "id",
            "acno",
            "accname",
            "accname_ar",
            "grpcode",
            "baltype",
            "actype",
            "acmapno",
            "opening_balance",
            "curbal",

            "organization",
            "organization_name",
            "branches",
            "branch_names",

            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [ "id", "acno", "acmapno", "created_by", "updated_by", "created_at", "updated_at"]
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    # ------------------ VALIDATION ------------------
    def validate(self, data):
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)


# ----------------------- Account Master Mapping Serializer -----------------------
from apps.purchase.models import ACCT_MAST_MAP

class ACCTMASTMAPSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ACCT_MAST_MAP
        fields = [
            "id",
            "acmapno",
            "totlev",
            "lev1", "lev2", "lev3", "lev4", "lev5", "lev6", "lev7", "lev8",

            "organization",
            "organization_name",
            "branches",
            "branch_names",

            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [ "id", "acmapno", "created_by", "updated_by", "created_at", "updated_at"]
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]

    def validate(self, data):
        """
        Ensure totlev matches levels provided.
        Example: If totlev=3 → lev1, lev2, lev3 must be present.
        """
        totlev = data.get("totlev", getattr(self.instance, "totlev", 1))

        # Collect all level values
        levels = [
            data.get("lev1"),
            data.get("lev2"),
            data.get("lev3"),
            data.get("lev4"),
            data.get("lev5"),
            data.get("lev6"),
            data.get("lev7"),
            data.get("lev8"),
        ]

        # Required levels must not be None
        required_levels = levels[:totlev]
        if any(l is None for l in required_levels):
            raise serializers.ValidationError(
                f"Levels lev1 to lev{totlev} must be provided when totlev = {totlev}"
            )
        
        #Organization and Branch validation
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())
        
        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data
    
    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        instance = super().update(instance, validated_data)

        totlev = validated_data.get("totlev", instance.totlev)

        level_fields = ["lev1","lev2","lev3","lev4","lev5","lev6","lev7","lev8"]

        for idx, field in enumerate(level_fields):
            if idx + 1 > totlev:
                setattr(instance, field, None)

        instance.save()

        return instance


# ----------------------- Account Transaction Detail Serializer -----------------------
from .models import ACC_TRAN_DETA

class ACCTRANDETASerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    vr_type_name = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()
    acc_tran_vrno = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    class Meta:
        model = ACC_TRAN_DETA
        fields = [
            "id",
            "acc_tran",
            "acc_tran_vrno",
            "voucher_date",
            "vr_type",
            "vr_type_name",
            "serial_no",
            "dc_flag",
            "account",
            "account_name",
            "list_code_ac",
            "amount",
            "remark",
            "organization",
            "organization_name",
            "branches",
            "branch_names",
            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "serial_no",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.CharField())
    def get_vr_type_name(self, obj):
        return obj.vr_type.vrname if obj.vr_type else None

    @extend_schema_field(serializers.CharField())
    def get_account_name(self, obj):
        return obj.account.accname if obj.account else None

    @extend_schema_field(serializers.CharField())
    def get_acc_tran_vrno(self, obj):
        return obj.acc_tran.vrno if obj.acc_tran else None
    
        # ------------------ DISPLAY FIELDS ------------------
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
        return [branch.name for branch in obj.branches.all()]
    
    
    # ------------------ VALIDATION ------------------
    def validate(self, data):

        # Validate: acc_tran exists
        acc_tran = data.get("acc_tran")
        if not acc_tran:
            raise serializers.ValidationError("acc_tran (Account Transaction) is required.")

        # Validate VR Type
        vr_type = data.get("vr_type")
        if vr_type and not VRTypeMaster.objects.filter(id=vr_type.id).exists():
            raise serializers.ValidationError("Invalid VR Type.")

        # Validate Account Master (acno)
        acno = data.get("acno")
        if acno and not ACCT_MAST.objects.filter(id=acno.id).exists():
            raise serializers.ValidationError("Invalid ACCT_MAST (acno).")
        
        organization = data.get("organization", getattr(self.instance, "organization", None))
        branches = data.get("branches")

        # convert to list if ManyToManyQuerySet
        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                b for b in branches
                if not self.branch_belongs_to_org(b, organization)
            ]
            if invalid_branches:
                br_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do NOT belong to organization '{organization.name}': {br_names}"
                )

        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization

    # ------------------ CREATE ------------------
    def create(self, validated_data):
        validated_data = self.assign_org_branch_on_create(validated_data)

        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)

    # ------------------ UPDATE ------------------
    def update(self, instance, validated_data):
        instance = self.assign_org_branch_on_update(instance, validated_data)

        user = self.context["request"].user
        instance.updated_by = user

        return super().update(instance, validated_data)



# ----------------------- Purchase Invoice Line Serializer -----------------------
from .models import PurchaseInvoiceLine

class PurchaseInvoiceLineSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseInvoiceLine
        fields = [
            "id", "item", "item_name", "unit", "unit_name",
            "qty", "rate", "amount",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "amount", "created_at", "updated_at"]

    @extend_schema_field(serializers.CharField())
    def get_item_name(self, obj):
        return obj.item.itname if obj.item else None

    @extend_schema_field(serializers.CharField())
    def get_unit_name(self, obj):
        return obj.unit.unitname if obj.unit else None


# ----------------------- Purchase Invoice Serializer -----------------------
from .models import PurchaseInvoice

class PurchaseInvoiceSerializer(OrgBranchAssignMixin, serializers.ModelSerializer):
    lines = PurchaseInvoiceLineSerializer(many=True, required=False)
    supplier_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseInvoice
        fields = [
            "id", "invoice_no", "supplier", "supplier_name",
            "vr_type", "vat", "invoice_date", "due_date",
            "reference_no", "paymode", "status",
            "amount_ex_vat", "vat_amount", "amount_inc_vat",
            "narration", "is_active", "lines",
            "organization", "organization_name",
            "branches", "branch_names",
            "created_by", "created_by_name",
            "updated_by", "updated_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "invoice_no", "vat_amount", "amount_inc_vat",
            "created_at", "updated_at", "created_by", "updated_by",
        ]

    @extend_schema_field(serializers.CharField())
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(serializers.ListSerializer(child=serializers.CharField()))
    def get_branch_names(self, obj):
        return [b.name for b in obj.branches.all()]

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def create(self, validated_data):
        from django.db import transaction
        lines_data = validated_data.pop("lines", [])
        validated_data = self.assign_org_branch_on_create(validated_data)
        branches = validated_data.pop("branches", [])
        user = self.context["request"].user
        validated_data["created_by"] = user

        with transaction.atomic():
            invoice = PurchaseInvoice.objects.create(**validated_data)
            if branches:
                invoice.branches.set(branches)
            for line in lines_data:
                PurchaseInvoiceLine.objects.create(
                    invoice=invoice,
                    organization=invoice.organization,
                    created_by=user,
                    **line,
                )
        return invoice

    def update(self, instance, validated_data):
        from django.db import transaction
        lines_data = validated_data.pop("lines", None)
        instance = self.assign_org_branch_on_update(instance, validated_data)
        user = self.context["request"].user
        instance.updated_by = user

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if lines_data is not None:
                instance.lines.all().delete()
                for line in lines_data:
                    PurchaseInvoiceLine.objects.create(
                        invoice=instance,
                        organization=instance.organization,
                        updated_by=user,
                        **line,
                    )
        return instance
