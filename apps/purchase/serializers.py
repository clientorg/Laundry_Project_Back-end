from rest_framework import serializers

#-------------------------- VAT Master Serializer --------------------------
from .models import VATMaster
class VATMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VATMaster
        fields = [
            "vatid",
            "vatname",
            "vatnamear",
            "vatper",
            "accestat",
            "organization",
            "branch",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "vatid","created_at","updated_at","created_by","updated_by",]

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

            "accestat",

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


