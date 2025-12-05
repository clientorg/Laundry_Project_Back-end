from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.organizations.mixins import OrgBranchQuerysetMixin

# ------------------------------- VAT Master ViewSet -------------------------------
from .models import VATMaster
from .serializers import VATMasterSerializer

@extend_schema_view(
    list=extend_schema(summary="List VAT Masters",description="Fetch all VAT records.",tags=["Purchase: VAT Master"],),
    retrieve=extend_schema(summary="Retrieve VAT Master",description="Get a VAT record by ID.",tags=["Purchase: VAT Master"],),
    create=extend_schema(summary="Create VAT Master",description="Insert a new VAT record.",tags=["Purchase: VAT Master"],),
    update=extend_schema(summary="Update VAT Master",description="Fully update a VAT record.",tags=["Purchase: VAT Master"],),
    partial_update=extend_schema(summary="Partially Update VAT Master",description="Update specific fields of a VAT record.",tags=["Purchase: VAT Master"],),
    destroy=extend_schema(summary="Delete VAT Master",description="Delete a VAT record by ID.",tags=["Purchase: VAT Master"],),
)
class VATMasterViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = VATMaster.objects.all().order_by("-created_at")
    serializer_class = VATMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_vatmaster",
        "POST": "purchase.add_vatmaster",
        "PUT": "purchase.change_vatmaster",
        "PATCH": "purchase.change_vatmaster",
        "DELETE": "purchase.delete_vatmaster",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ------------------------------- Supplier Master ViewSet ------------------------------
from .models import SupplierMaster
from .serializers import SupplierMasterSerializer

@extend_schema_view(
    list=extend_schema(summary="List Suppliers",tags=["Purchase: Supplier Master"]),
    create=extend_schema(summary="Create Supplier",tags=["Purchase: Supplier Master"]),
    retrieve=extend_schema(summary="Get Supplier",tags=["Purchase: Supplier Master"]),
    update=extend_schema(summary="Update Supplier",tags=["Purchase: Supplier Master"]),
    partial_update=extend_schema(summary="Patch Supplier",tags=["Purchase: Supplier Master"]),
    destroy=extend_schema(summary="Delete Supplier",tags=["Purchase: Supplier Master"]),
)
class SupplierMasterViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = SupplierMaster.objects.all().order_by("-id")
    serializer_class = SupplierMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_suppliermaster",
        "POST": "purchase.add_suppliermaster",
        "PUT": "purchase.change_suppliermaster",
        "PATCH": "purchase.change_suppliermaster",
        "DELETE": "purchase.delete_suppliermaster",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ------------------------------- Group Master ViewSet ------------------------------
from .models import GroupMaster
from .serializers import GroupMasterSerializer

@extend_schema_view(
    list=extend_schema(summary="List Group Masters",description="Fetch all Group Master records.",tags=["Purchase: Group Master"],),
    retrieve=extend_schema(summary="Retrieve Group Master",description="Get a Group Master record by ID.",tags=["Purchase: Group Master"],),
    create=extend_schema(summary="Create Group Master",description="Insert a new Group Master record.",tags=["Purchase: Group Master"],),
    update=extend_schema(summary="Update Group Master",description="Fully update a Group Master record.",tags=["Purchase: Group Master"],),
    partial_update=extend_schema(summary="Partially Update Group Master",description="Update specific fields of a Group Master record.",tags=["Purchase: Group Master"],),
    destroy=extend_schema(summary="Delete Group Master",description="Delete a Group Master record by ID.",tags=["Purchase: Group Master"],),
)
class GroupMasterViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = GroupMaster.objects.all().order_by("-id")
    serializer_class = GroupMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_groupmaster",
        "POST": "purchase.add_groupmaster",
        "PUT": "purchase.change_groupmaster",
        "PATCH": "purchase.change_groupmaster",
        "DELETE": "purchase.delete_groupmaster",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ------------------------------- Brand Master ViewSet ------------------------------
from .models import BrandMaster
from .serializers import BrandMasterSerializer
@extend_schema_view(
    list=extend_schema(summary="List Brand Masters",description="Fetch all Brand Master records.",tags=["Purchase: Brand Master"],),
    retrieve=extend_schema(summary="Retrieve Brand Master",description="Get a Brand Master record by ID.",tags=["Purchase: Brand Master"],),
    create=extend_schema(summary="Create Brand Master",description="Insert a new Brand Master record.",tags=["Purchase: Brand Master"],),
    update=extend_schema(summary="Update Brand Master",description="Fully update a Brand Master record.",tags=["Purchase: Brand Master"],),
    partial_update=extend_schema(summary="Partially Update Brand Master",description="Update specific fields of a Brand Master record.",tags=["Purchase: Brand Master"],),
    destroy=extend_schema(summary="Delete Brand Master",description="Delete a Brand Master record by ID.",tags=["Purchase: Brand Master"],),
)
class BrandMasterViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = BrandMaster.objects.all().order_by("-id")
    serializer_class = BrandMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_brandmaster",
        "POST": "purchase.add_brandmaster",
        "PUT": "purchase.change_brandmaster",
        "PATCH": "purchase.change_brandmaster",
        "DELETE": "purchase.delete_brandmaster",
    }


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ------------------------------- ITGRP_MAP ViewSet ------------------------------
from .models import ITGRP_MAP
from .serializers import ITGRP_MAPSerializer

@extend_schema_view(
    list=extend_schema(summary="List IT Group Mappings",description="Fetch all ITGRP_MAP records.",tags=["Purchase: ITGRP_MAP"],),
    retrieve=extend_schema(summary="Retrieve IT Group Mapping",description="Get a specific ITGRP_MAP record by ID.",tags=["Purchase: ITGRP_MAP"],),
    create=extend_schema(summary="Create IT Group Mapping",description="Insert a new ITGRP_MAP record.",tags=["Purchase: ITGRP_MAP"],),
    update=extend_schema(summary="Update IT Group Mapping",description="Fully update an existing ITGRP_MAP record.",tags=["Purchase: ITGRP_MAP"],),
    partial_update=extend_schema(summary="Partially Update IT Group Mapping",description="Update selected fields of an ITGRP_MAP record.",tags=["Purchase: ITGRP_MAP"],),
    destroy=extend_schema(summary="Delete IT Group Mapping",description="Delete an ITGRP_MAP record by ID.",tags=["Purchase: ITGRP_MAP"],),
)
class ITGRP_MAPViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = ITGRP_MAP.objects.all().order_by("-id")
    serializer_class = ITGRP_MAPSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_itgrp_map",
        "POST": "purchase.add_itgrp_map",
        "PUT": "purchase.change_itgrp_map",
        "PATCH": "purchase.change_itgrp_map",
        "DELETE": "purchase.delete_itgrp_map",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

# ----------------------- Unit Master ViewSet -----------------------
from .models import UnitMaster
from .serializers import UnitMasterSerializer

@extend_schema_view(
    list=extend_schema(summary="List Units",description="Fetch all UnitMaster records.",tags=["Purchase: Unit Master"],),
    retrieve=extend_schema(summary="Retrieve Unit",description="Get a UnitMaster record by ID.",tags=["Purchase: Unit Master"],),
    create=extend_schema(summary="Create Unit",description="Insert a new UnitMaster record.",tags=["Purchase: Unit Master"],),
    update=extend_schema(summary="Update Unit",description="Fully update an existing UnitMaster record.",tags=["Purchase: Unit Master"],),
    partial_update=extend_schema(summary="Partially Update Unit",description="Update selected fields of a UnitMaster record.",tags=["Purchase: Unit Master"],),
    destroy=extend_schema(summary="Delete Unit",description="Delete a UnitMaster record by ID.",tags=["Purchase: Unit Master"],),
)
class UnitMasterViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = UnitMaster.objects.all().order_by("-id")
    serializer_class = UnitMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_unitmaster",
        "POST": "purchase.add_unitmaster",
        "PUT": "purchase.change_unitmaster",
        "PATCH": "purchase.change_unitmaster",
        "DELETE": "purchase.delete_unitmaster",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)



# ----------------------- Item Master ViewSet -----------------------
from .models import ItemMaster
from .serializers import ItemMasterSerializer
@extend_schema_view(
    list=extend_schema(summary="List Items",description="Fetch all ItemMaster records.",tags=["Purchase: Item Master"],),
    retrieve=extend_schema(summary="Retrieve Item",description="Get an ItemMaster record by ID.",tags=["Purchase: Item Master"],),
    create=extend_schema(summary="Create Item",description="Insert a new ItemMaster record.",tags=["Purchase: Item Master"],),
    update=extend_schema(summary="Update Item",description="Fully update an existing ItemMaster record.",tags=["Purchase: Item Master"],),
    partial_update=extend_schema(summary="Partially Update Item",description="Update selected fields of an ItemMaster record.",tags=["Purchase: Item Master"],),
    destroy=extend_schema(summary="Delete Item",description="Delete an ItemMaster record by ID.",tags=["Purchase: Item Master"],),
)
class ItemMasterViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = ItemMaster.objects.all().order_by("-id")
    serializer_class = ItemMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_itemmaster",
        "POST": "purchase.add_itemmaster",
        "PUT": "purchase.change_itemmaster",
        "PATCH": "purchase.change_itemmaster",
        "DELETE": "purchase.delete_itemmaster",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ----------------------- Unit Map ViewSet -----------------------
from .models import UnitMap
from .serializers import UnitMapSerializer

@extend_schema_view(
    list=extend_schema(summary="List Unit Maps",description="Fetch all UnitMap records.",tags=["Purchase: Unit Map"],),
    retrieve=extend_schema(summary="Retrieve Unit Map",description="Get a UnitMap record by ID.",tags=["Purchase: Unit Map"],),
    create=extend_schema(summary="Create Unit Map",description="Insert a new UnitMap record.",tags=["Purchase: Unit Map"],),
    update=extend_schema(summary="Update Unit Map",description="Fully update an existing UnitMap record.",tags=["Purchase: Unit Map"],),
    partial_update=extend_schema(summary="Partially Update Unit Map",description="Update selected fields of a UnitMap record.",tags=["Purchase: Unit Map"],),
    destroy=extend_schema(summary="Delete Unit Map",description="Delete a UnitMap record by ID.",tags=["Purchase: Unit Map"],),
)
class UnitMapViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = UnitMap.objects.all().order_by("-id")
    serializer_class = UnitMapSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_unitmap",
        "POST": "purchase.add_unitmap",
        "PUT": "purchase.change_unitmap",
        "PATCH": "purchase.change_unitmap",
        "DELETE": "purchase.delete_unitmap",
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ----------------------- VR Type Master ViewSet -----------------------
from .models import VRTypeMaster
from .serializers import VRTypeMasterSerializer

@extend_schema_view(
    list=extend_schema(summary="List VR Types",description="Fetch all VR Type records.",tags=["Purchase: VRType Master"],),
    create=extend_schema(summary="Create VR Type",description="Add a new VR Type.",tags=["Purchase: VRType Master"],),
    retrieve=extend_schema(summary="Retrieve VR Type",description="Get VR Type by ID.",tags=["Purchase: VRType Master"],),
    update=extend_schema(summary="Update VR Type",description="Replace VR Type completely.",tags=["Purchase: VRType Master"],),
    partial_update=extend_schema(summary="Patch VR Type",description="Update specific VR Type fields.",tags=["Purchase: VRType Master"],),
    destroy=extend_schema(summary="Delete VR Type",description="Delete VR Type by ID.",tags=["Purchase: VRType Master"],),
)
class VRTypeMasterViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = VRTypeMaster.objects.all().order_by("-id")
    serializer_class = VRTypeMasterSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_vrtypemaster",
        "POST": "purchase.add_vrtypemaster",
        "PUT": "purchase.change_vrtypemaster",
        "PATCH": "purchase.change_vrtypemaster",
        "DELETE": "purchase.delete_vrtypemaster",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ----------------------- INV_TRAN ViewSet -----------------------
from .models import INV_TRAN
from .serializers import INVTRANSerializer


@extend_schema_view(
    list=extend_schema(summary="List Inventory Transactions",description="Fetch all INV_TRAN records.",tags=["Purchase: INV_TRAN"],),
    retrieve=extend_schema(summary="Retrieve Inventory Transaction",description="Get INV_TRAN by ID.",tags=["Purchase: INV_TRAN"],),
    create=extend_schema(summary="Create Inventory Transaction",description="Insert new INV_TRAN entry.",tags=["Purchase: INV_TRAN"],),
    update=extend_schema(summary="Update Inventory Transaction",description="Fully update INV_TRAN record.",tags=["Purchase: INV_TRAN"],),
    partial_update=extend_schema(summary="Partially Update Inventory Transaction",description="Update selected fields.",tags=["Purchase: INV_TRAN"],),
    destroy=extend_schema(summary="Delete Inventory Transaction",description="Delete INV_TRAN by ID.",tags=["Purchase: INV_TRAN"],),
)
class INVTRANViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = INV_TRAN.objects.all().order_by("-id")
    serializer_class = INVTRANSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_inv_tran",
        "POST": "purchase.add_inv_tran",
        "PUT": "purchase.change_inv_tran",
        "PATCH": "purchase.change_inv_tran",
        "DELETE": "purchase.delete_inv_tran",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ----------------------- ACC_TRAN ViewSet -----------------------
from .models import ACC_TRAN
from .serializers import ACCTRANSerializer

@extend_schema_view(
    list=extend_schema(summary="List Account Transactions",description="Fetch all ACC_TRAN entries.",tags=["Purchase: ACC_TRAN"],),
    retrieve=extend_schema(summary="Retrieve Account Transaction",description="Get a single ACC_TRAN by ID.",tags=["Purchase: ACC_TRAN"],),
    create=extend_schema(summary="Create Account Transaction",description="Insert a new ACC_TRAN record.",tags=["Purchase: ACC_TRAN"],),
    update=extend_schema(summary="Update Account Transaction",description="Fully update an ACC_TRAN record.",tags=["Purchase: ACC_TRAN"],),
    partial_update=extend_schema(summary="Patch Account Transaction",description="Partially update an ACC_TRAN record.",tags=["Purchase: ACC_TRAN"],),
    destroy=extend_schema(summary="Delete Account Transaction",description="Delete an ACC_TRAN entry by ID.",tags=["Purchase: ACC_TRAN"],),
)
class ACC_TRANViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = ACC_TRAN.objects.all().order_by("-created_at")
    serializer_class = ACCTRANSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_acc_tran",
        "POST": "purchase.add_acc_tran",
        "PUT": "purchase.change_acc_tran",
        "PATCH": "purchase.change_acc_tran",
        "DELETE": "purchase.delete_acc_tran",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ----------------------- ACCT_MAST ViewSet -----------------------
from .models import ACCT_MAST
from .serializers import ACCTMASTSerializer

@extend_schema_view(
    list=extend_schema(summary="List Account Masters",description="Retrieve all account master records.",tags=["Purchase: Account Master"]),
    retrieve=extend_schema(summary="Get Account Master",description="Retrieve a single account master by ID.",tags=["Purchase: Account Master"]),
    create=extend_schema(summary="Create Account Master",description="Create a new account master record.",tags=["Purchase: Account Master"]),
    update=extend_schema(summary="Update Account Master",description="Fully update an existing account master.",tags=["Purchase: Account Master"]),
    partial_update=extend_schema(summary="Partially Update Account Master",description="Update selected fields in account master.",tags=["Purchase: Account Master"]),
    destroy=extend_schema(summary="Delete Account Master",description="Delete an account master by ID.",tags=["Purchase: Account Master"]),
)
class ACCTMASTViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = ACCT_MAST.objects.all().order_by("acno")
    serializer_class = ACCTMASTSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_acct_mast",
        "POST": "purchase.add_acct_mast",
        "PUT": "purchase.change_acct_mast",
        "PATCH": "purchase.change_acct_mast",
        "DELETE": "purchase.delete_acct_mast",
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    

# ----------------------- ACCT_MAST_MAP ViewSet -----------------------
from .models import ACCT_MAST_MAP
from .serializers import ACCTMASTMAPSerializer

@extend_schema_view(
    list=extend_schema(summary="List Account Master Mappings",description="Fetch all ACCT_MAST_MAP entries.",tags=["Purchase: ACCT_MAST_MAP"],),
    retrieve=extend_schema(summary="Retrieve Account Master Mapping",description="Get a single ACCT_MAST_MAP record.",tags=["Purchase: ACCT_MAST_MAP"],),
    create=extend_schema(summary="Create Account Master Mapping",description="Insert a new ACCT_MAST_MAP record.",tags=["Purchase: ACCT_MAST_MAP"],),
    update=extend_schema(summary="Update Account Master Mapping",description="Update an ACCT_MAST_MAP entry.",tags=["Purchase: ACCT_MAST_MAP"],),
    partial_update=extend_schema(summary="Patch Account Master Mapping",description="Partially update an ACCT_MAST_MAP entry.",tags=["Purchase: ACCT_MAST_MAP"],),
    destroy=extend_schema(summary="Delete Account Master Mapping",description="Delete an ACCT_MAST_MAP entry.",tags=["Purchase: ACCT_MAST_MAP"],),
)
class ACCT_MAST_MAPViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = ACCT_MAST_MAP.objects.all().order_by("acmapno")
    serializer_class = ACCTMASTMAPSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_acct_mast_map",
        "POST": "purchase.add_acct_mast_map",
        "PUT": "purchase.change_acct_mast_map",
        "PATCH": "purchase.change_acct_mast_map",
        "DELETE": "purchase.delete_acct_mast_map",
    }
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ----------------------- ACC_TRAN_DETA ViewSet -----------------------
from apps.purchase.models import ACC_TRAN_DETA
from apps.purchase.serializers import ACCTRANDETASerializer

@extend_schema_view(
    list=extend_schema(summary="List ACC_TRAN_DETA",description="Fetch all account transaction detail entries.",tags=["Purchase: ACC_TRAN_DETA"],),
    retrieve=extend_schema(summary="Retrieve ACC_TRAN_DETA",description="Fetch a single ACC_TRAN_DETA record by ID.",tags=["Purchase: ACC_TRAN_DETA"],),
    create=extend_schema(summary="Create ACC_TRAN_DETA",description="Insert a new account transaction detail line.",tags=["Purchase: ACC_TRAN_DETA"],),
    update=extend_schema(summary="Update ACC_TRAN_DETA",description="Fully update an account transaction detail line.",tags=["Purchase: ACC_TRAN_DETA"],),
    partial_update=extend_schema(summary="Patch ACC_TRAN_DETA",description="Partially update an account transaction detail line.",tags=["Purchase: ACC_TRAN_DETA"],),
    destroy=extend_schema(summary="Delete ACC_TRAN_DETA",description="Delete an account transaction detail line.",tags=["Purchase: ACC_TRAN_DETA"],),
)
class ACC_TRAN_DETAViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = ACC_TRAN_DETA.objects.all().order_by("-acc_tran__created_at")
    serializer_class = ACCTRANDETASerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "purchase.view_acc_tran_deta",
        "POST": "purchase.add_acc_tran_deta",
        "PUT": "purchase.change_acc_tran_deta",
        "PATCH": "purchase.change_acc_tran_deta",
        "DELETE": "purchase.delete_acc_tran_deta",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)