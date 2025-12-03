from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

#-------------------------- VAT Master Serializer --------------------------
from .models import VATMaster
class VATMasterSerializer(serializers.ModelSerializer):
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
            "branch",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ['id', "vatid","created_at","updated_at","created_by","updated_by",]

#----------------------- Supplier Master Serializer -----------------------
from .models import SupplierMaster
class SupplierMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierMaster
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


#----------------------- Group Master Serializer -----------------------
from .models import GroupMaster
class GroupMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMaster
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


#----------------------- Brand Master Serializer -----------------------
from .models import BrandMaster
class BrandMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandMaster
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


#----------------------- ITGRP_MAP Serializer -----------------------
from .models import ITGRP_MAP
class ITGRP_MAPSerializer(serializers.ModelSerializer):
    grpname = serializers.SerializerMethodField()
    brdname = serializers.SerializerMethodField()

    class Meta:
        model = ITGRP_MAP
        fields = [
            "id",
            "organization",
            "branch",
            "grpcode",
            "grpname",
            "brdcode",
            "brdname",
            "is_active",
            "created_by",
            "updated_by",
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


#----------------------- Unit Master Serializer -----------------------
from .models import UnitMaster
class UnitMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMaster
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]


# ----------------------- Item Master Serializer -----------------------
from .models import ItemMaster

class ItemMasterSerializer(serializers.ModelSerializer):
    unit_name = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    vat_name = serializers.SerializerMethodField()

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
            "branch",

            "created_by",
            "updated_by",
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


# ----------------------- Unit Map Serializer -----------------------
from .models import UnitMap

class UnitMapSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    alt_unit_name = serializers.SerializerMethodField()

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
            "branch",
            "created_by",
            "updated_by",
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


# ----------------------- VR Type Master Serializer -----------------------
from .models import VRTypeMaster
class VRTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VRTypeMaster
        fields = "__all__"
        read_only_fields = ("id", "created_at", "created_by", "updated_by", "updated_at")


# ----------------------- Inventory Transaction Serializer -----------------------
from .models import INV_TRAN

class INVTRANSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    item_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    vr_type_name = serializers.SerializerMethodField()

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
            "branch",
            "is_active",
            "created_by",
            "updated_by",
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


# ----------------------- Account Transaction Serializer -----------------------
from .models import ACC_TRAN

class ACCTRANSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    vr_type_name = serializers.SerializerMethodField()
    vat_name = serializers.SerializerMethodField()

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
            "branch",
            "country",

            "is_active",
            "created_by",
            "updated_by",
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


# ----------------------- Account Master Serializer -----------------------
from .models import ACCT_MAST

class ACCTMASTSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ACCT_MAST
        fields = "__all__"
        read_only_fields = [ "id", "acno", "acmapno", "created_by", "updated_by", "created_at", "updated_at"]


# ----------------------- Account Master Mapping Serializer -----------------------
from apps.purchase.models import ACCT_MAST_MAP

class ACCTMASTMAPSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ACCT_MAST_MAP
        fields = "__all__"
        read_only_fields = [ "id", "acmapno", "created_by", "updated_by", "created_at", "updated_at"]

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

        return data
    
    def update(self, instance, validated_data):
        totlev = validated_data.get("totlev", instance.totlev)

        # Update normal fields
        instance = super().update(instance, validated_data)

        # Clear unused levels
        level_fields = ["lev1","lev2","lev3","lev4","lev5","lev6","lev7","lev8"]

        for idx, field in enumerate(level_fields):
            if idx + 1 > totlev:
                setattr(instance, field, None)

        instance.save()
        return instance


# ----------------------- Account Transaction Detail Serializer -----------------------
from .models import ACC_TRAN_DETA

class ACCTRANDETASerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    vr_type_name = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()
    acc_tran_vrno = serializers.SerializerMethodField()

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
            "branch",
            "is_active",
            "created_by",
            "updated_by",
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
    
    # VALIDATION
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

        return data

