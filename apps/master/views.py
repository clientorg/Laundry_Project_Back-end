from django.shortcuts import render

# package imports
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry mixin imports
from apps.master.backup_service import DatabaseBackupService
from apps.organizations.mixins import OrgBranchQuerysetMixin

# laundry permission validator
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

# laundry model imports
from apps.orders.models import OrderItem
from .models import Country, Item, ClothType, ServiceType, HandlingType, DeliveryType

# laundry serializer imports
from .serializers import (
    CountrySerializer,
    ItemSerializer,
    ClothTypeSerializer,
    ServiceTypeSerializer,
    HandlingTypeSerializer,
    DeliveryTypeSerializer,
)


# Create your views here.
# master views
@extend_schema(tags=["Master"])
class CountryMasterView(generics.ListAPIView):
    serializer_class = CountrySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Country.objects.all().order_by("name")
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)


# item views
@extend_schema(tags=["Items"])
class ItemListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    permission_map = {
        "GET": "master.view_item",
        "POST": "master.add_item",
    }


@extend_schema(tags=["Items"])
class ItemRetrieveUpdateDestroyView(
    PermissionRequiredMixin,
    OrgBranchQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [MultiPartParser, FormParser]

    permission_map = {
        "GET": "master.view_item",
        "PUT": "master.change_item",
        "PATCH": "master.change_item",
        "DELETE": "master.delete_item",
    }

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        is_used = OrderItem.objects.filter(
            cloth_name=instance.name, order__payments__isnull=False
        ).exists()

        if is_used:
            return Response(
                {
                    "detail": "Cannot delete this item. It is used in one or more paid orders."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Items"])
class ItemClothOnlyView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_size_based_price=False, is_active=True)


@extend_schema(tags=["Items"])
class ItemClothOnlyPinnedView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_pinned=True, is_size_based_price=False, is_active=True)


@extend_schema(tags=["Items"])
class ItemClothOnlyStartsWithView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        letter = self.kwargs.get("letter")
        return qs.filter(
            name__istartswith=letter, is_size_based_price=False, is_active=True
        )


@extend_schema(tags=["Items"])
class ItemCarpetOnlyView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_size_based_price=True, is_active=True)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyPinnedView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_pinned=True, is_size_based_price=True, is_active=True)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyStartsWithView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        letter = self.kwargs.get("letter")
        return qs.filter(
            name__istartswith=letter, is_size_based_price=True, is_active=True
        )


# cloth type views
@extend_schema(tags=["Cloth Types"])
class ClothTypeListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    permission_map = {
        "GET": "master.view_clothtype",
        "POST": "master.add_clothtype",
    }


@extend_schema(tags=["Cloth Types"])
class ClothTypeClothOnlyView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_carpet=False)


@extend_schema(tags=["Cloth Types"])
class ClothTypeStartsWithView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        letter = self.kwargs.get("letter")
        return qs.filter(name__istartswith=letter, is_carpet=False)


@extend_schema(tags=["Cloth Types"])
class ClothTypePinnedView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_pinned=True, is_carpet=False)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetOnlyView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_carpet=True)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetStartsWithView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        letter = self.kwargs.get("letter")
        return qs.filter(name__istartswith=letter, is_carpet=True)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetPinnedView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_pinned=True, is_carpet=True)


@extend_schema(tags=["Cloth Types"])
class ClothTypeRetrieveView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.RetrieveAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_clothtype",
    }


@extend_schema(tags=["Cloth Types"])
class ClothTypeUpdateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.UpdateAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_clothtype",
        "PATCH": "master.change_clothtype",
    }


@extend_schema(tags=["Cloth Types"])
class ClothTypeDeleteView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.DestroyAPIView
):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_clothtype",
    }


# service type views
@extend_schema(tags=["Service Types"])
class ServiceTypeListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_servicetype",
        "POST": "master.add_servicetype",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("name")


@extend_schema(tags=["Service Types"])
class ServiceTypeListInwardView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by("name")


@extend_schema(tags=["Service Types"])
class ServiceTypeDetailView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.RetrieveAPIView
):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.add_servicetype",
    }


@extend_schema(tags=["Service Types"])
class ServiceTypeUpdateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.UpdateAPIView
):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_servicetype",
        "PATCH": "master.change_servicetype",
    }


@extend_schema(tags=["Service Types"])
class ServiceTypeDeleteView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.DestroyAPIView
):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_servicetype",
    }


# handling type views
@extend_schema(tags=["Handling Types"])
class HandlingTypeListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_handlingtype",
        "POST": "master.add_handlingtype",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("name")


@extend_schema(tags=["Handling Types"])
class HandlingTypeListInwardView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by("name")


@extend_schema(tags=["Handling Types"])
class HandlingTypeDetailView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.RetrieveAPIView
):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_handlingtype",
    }


@extend_schema(tags=["Handling Types"])
class HandlingTypeUpdateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.UpdateAPIView
):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_handlingtype",
        "PATCH": "master.change_handlingtype",
    }


@extend_schema(tags=["Handling Types"])
class HandlingTypeDeleteView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.DestroyAPIView
):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_handlingtype",
    }


# delivery type views
@extend_schema(tags=["Delivery Types"])
class DeliveryTypeListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = DeliveryType.objects.all().order_by("name")
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_deliverytype",
        "POST": "master.add_deliverytype",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeListInwardView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by("name")


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeDetailView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.RetrieveAPIView
):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_deliverytype",
    }


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeUpdateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.UpdateAPIView
):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_deliverytype",
        "PATCH": "master.change_deliverytype",
    }


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeDeleteView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.DestroyAPIView
):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_deliverytype",
    }


@extend_schema(tags=["Database Backup"])
class DatabaseBackupView(
    PermissionRequiredMixin,
    generics.ListCreateAPIView,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        HasAccessPermission,
    ]

    permission_map = {
        "GET": "api_view_database_backup",
        "POST": "api_add_database_backup",
    }

    def list(self, request, *args, **kwargs):
        try:
            backups = DatabaseBackupService.list_backups()

            return Response(
                {
                    "status": 1,
                    "message": "Backups retrieved successfully.",
                    "backup_directory": str(DatabaseBackupService.get_backup_dir()),
                    "count": len(backups),
                    "backups": backups,
                }
            )

        except Exception as exc:
            return Response(
                {
                    "status": 0,
                    "message": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        try:
            backup = DatabaseBackupService.create_backup()

            return Response(
                {
                    "status": 1,
                    "message": "Database backup created successfully.",
                    "backup": backup,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:
            return Response(
                {
                    "status": 0,
                    "message": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Database Backup"])
class DatabaseBackupRestoreView(
    PermissionRequiredMixin,
    generics.GenericAPIView,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        HasAccessPermission,
    ]

    permission_map = {
        "POST": "api_restore_database_backup",
    }

    def post(self, request, *args, **kwargs):
        filename = request.data.get("filename")

        if not filename:
            return Response(
                {
                    "status": 0,
                    "message": "Backup filename is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            DatabaseBackupService.restore_backup(filename)

            return Response(
                {
                    "status": 1,
                    "message": "Database restored successfully.",
                    "filename": filename,
                }
            )

        except FileNotFoundError as exc:
            return Response(
                {
                    "status": 0,
                    "message": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as exc:
            return Response(
                {
                    "status": 0,
                    "message": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Database Backup"])
class DatabaseBackupDeleteView(
    PermissionRequiredMixin,
    generics.DestroyAPIView,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        HasAccessPermission,
    ]

    permission_map = {
        "DELETE": "api_delete_database_backup",
    }

    def destroy(self, request, *args, **kwargs):
        filename = kwargs.get("filename")

        try:
            DatabaseBackupService.delete_backup(filename)

            return Response(
                {
                    "status": 1,
                    "message": "Backup deleted successfully.",
                    "filename": filename,
                }
            )

        except FileNotFoundError as exc:
            return Response(
                {
                    "status": 0,
                    "message": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as exc:
            return Response(
                {
                    "status": 0,
                    "message": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
