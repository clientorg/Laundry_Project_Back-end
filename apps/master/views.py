from django.shortcuts import render

# package imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication

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
class CountryMasterView(APIView):
    serializer_class = CountrySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Country.objects.all().order_by("name")
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)


# item views
@extend_schema(tags=["Items"])
class ItemListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = Item.objects.all().order_by("name")
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]
    parser_classes = [MultiPartParser, FormParser]

    permission_map = {
        "GET": "master.view_item",
        "POST": "master.add_item",
    }

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )


@extend_schema(tags=["Items"])
class ItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    permission_map = {
        "GET": "master.view_item",
        "PUT": "master.change_item",
        "PATCH": "master.change_item",
        "DELETE": "master.delete_item",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

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
class ItemClothOnlyView(PermissionRequiredMixin, APIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_size_based_price=False)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemClothOnlyPinnedView(PermissionRequiredMixin, APIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_pinned=True, is_size_based_price=False)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemClothOnlyStartsWithView(PermissionRequiredMixin, APIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = Item.objects.filter(
            name__istartswith=letter, is_size_based_price=False
        )
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyView(PermissionRequiredMixin, APIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_size_based_price=True)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyPinnedView(PermissionRequiredMixin, APIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_pinned=True, is_size_based_price=True)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyStartsWithView(PermissionRequiredMixin, APIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = Item.objects.filter(
            name__istartswith=letter, is_size_based_price=True
        )
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


# cloth type views
@extend_schema(tags=["Cloth Types"])
class ClothTypeListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = ClothType.objects.all().order_by("name")
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_clothtype",
        "POST": "master.add_clothtype",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Cloth Types"])
class ClothTypeClothOnlyView(PermissionRequiredMixin, APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_carpet=False)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeStartsWithView(PermissionRequiredMixin, APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = ClothType.objects.filter(name__istartswith=letter, is_carpet=False)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypePinnedView(PermissionRequiredMixin, APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_pinned=True, is_carpet=False)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetOnlyView(PermissionRequiredMixin, APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_carpet=True)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetStartsWithView(PermissionRequiredMixin, APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = ClothType.objects.filter(name__istartswith=letter, is_carpet=True)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetPinnedView(PermissionRequiredMixin, APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_pinned=True, is_carpet=True)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeRetrieveView(PermissionRequiredMixin, generics.RetrieveAPIView):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_clothtype",
    }


@extend_schema(tags=["Cloth Types"])
class ClothTypeUpdateView(PermissionRequiredMixin, generics.UpdateAPIView):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_clothtype",
        "PATCH": "master.change_clothtype",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Cloth Types"])
class ClothTypeDeleteView(PermissionRequiredMixin, generics.DestroyAPIView):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_clothtype",
    }


# service type views
@extend_schema(tags=["Service Types"])
class ServiceTypeListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = ServiceType.objects.all().order_by("name")
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_servicetype",
        "POST": "master.add_servicetype",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Service Types"])
class ServiceTypeListInwardView(PermissionRequiredMixin, APIView):
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = ServiceType.objects.all().order_by("name")
        serializer = ServiceTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Service Types"])
class ServiceTypeDetailView(PermissionRequiredMixin, generics.RetrieveAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.add_servicetype",
    }


@extend_schema(tags=["Service Types"])
class ServiceTypeUpdateView(PermissionRequiredMixin, generics.UpdateAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_servicetype",
        "PATCH": "master.change_servicetype",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Service Types"])
class ServiceTypeDeleteView(PermissionRequiredMixin, generics.DestroyAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_servicetype",
    }


# handling type views
@extend_schema(tags=["Handling Types"])
class HandlingTypeListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = HandlingType.objects.all().order_by("name")
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_handlingtype",
        "POST": "master.add_handlingtype",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Handling Types"])
class HandlingTypeListInwardView(PermissionRequiredMixin, APIView):
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = HandlingType.objects.all().order_by("name")
        serializer = HandlingTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Handling Types"])
class HandlingTypeDetailView(PermissionRequiredMixin, generics.RetrieveAPIView):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "master.view_handlingtype",
    }


@extend_schema(tags=["Handling Types"])
class HandlingTypeUpdateView(generics.UpdateAPIView):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_handlingtype",
        "PATCH": "master.change_handlingtype",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Handling Types"])
class HandlingTypeDeleteView(PermissionRequiredMixin, generics.DestroyAPIView):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_handlingtype",
    }


# delivery type views
@extend_schema(tags=["Delivery Types"])
class DeliveryTypeListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
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
class DeliveryTypeListInwardView(PermissionRequiredMixin, APIView):
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.add_order",
    }

    def get(self, request, letter, format=None):
        queryset = DeliveryType.objects.all().order_by("name")
        serializer = DeliveryTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeDetailView(PermissionRequiredMixin, generics.RetrieveAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    permission_map = {
        "GET": "master.view_deliverytype",
    }


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeUpdateView(PermissionRequiredMixin, generics.UpdateAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "PUT": "master.change_deliverytype",
        "PATCH": "master.change_deliverytype",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeDeleteView(PermissionRequiredMixin, generics.DestroyAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "DELETE": "master.delete_deliverytype",
    }
