from rest_framework import serializers

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
    class Meta:
        model = ITGRP_MAP
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]


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
            "group_map",
            "supplier",
            "vat",

            "is_active",

            "organization",
            "branch",

            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_by", "updated_by", "created_at", "updated_at"]


# ----------------------- Unit Map Serializer -----------------------
from .models import UnitMap

class UnitMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMap
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]


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

    class Meta:
        model = INV_TRAN
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]


# ----------------------- Account Transaction Serializer -----------------------
from .models import ACC_TRAN

class ACCTRANSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ACC_TRAN
        fields = "__all__"
        read_only_fields = [ "id", "vrno", "serial_no", "vat_amount", "amount_inc_vat", "created_by", "updated_by", "created_at", "updated_at"]


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


# ----------------------- Account Transaction Detail Serializer -----------------------
from .models import ACC_TRAN_DETA

class ACCTRANDETASerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ACC_TRAN_DETA
        fields = "__all__"
        read_only_fields = [
            "id",
            "serial_no",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

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

