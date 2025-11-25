from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view


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
class VATMasterViewSet(viewsets.ModelViewSet):
    queryset = VATMaster.objects.all().order_by("-created_at")
    serializer_class = VATMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class SupplierMasterViewSet(viewsets.ModelViewSet):
    queryset = SupplierMaster.objects.all().order_by("-id")
    serializer_class = SupplierMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class GroupMasterViewSet(viewsets.ModelViewSet):
    queryset = GroupMaster.objects.all().order_by("-id")
    serializer_class = GroupMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class BrandMasterViewSet(viewsets.ModelViewSet):
    queryset = BrandMaster.objects.all().order_by("-id")
    serializer_class = BrandMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class ITGRP_MAPViewSet(viewsets.ModelViewSet):
    queryset = ITGRP_MAP.objects.all().order_by("-id")
    serializer_class = ITGRP_MAPSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class UnitMasterViewSet(viewsets.ModelViewSet):
    queryset = UnitMaster.objects.all().order_by("-id")
    serializer_class = UnitMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class ItemMasterViewSet(viewsets.ModelViewSet):
    queryset = ItemMaster.objects.all().order_by("-id")
    serializer_class = ItemMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

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
class UnitMapViewSet(viewsets.ModelViewSet):
    queryset = UnitMap.objects.all().order_by("-id")
    serializer_class = UnitMapSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)