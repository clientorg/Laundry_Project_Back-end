from django.shortcuts import render

# package imports
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry model imports
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Country.objects.all().order_by("name")
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Master"])
class CountryMasterView(APIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Country.objects.all().order_by("name")
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)


# item views
@extend_schema(tags=["Items"])
class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all().order_by("name")
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Items"])
class ItemClothOnlyView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_size_based_price=False)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemClothOnlyPinnedView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_pinned=True, is_size_based_price=False)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemClothOnlyStartsWithView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, letter, format=None):
        queryset = Item.objects.filter(
            name__istartswith=letter, is_size_based_price=False
        )
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_size_based_price=True)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyPinnedView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = Item.objects.filter(is_pinned=True, is_size_based_price=True)
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Items"])
class ItemCarpetOnlyStartsWithView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, letter, format=None):
        queryset = Item.objects.filter(
            name__istartswith=letter, is_size_based_price=True
        )
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)


# cloth type views
@extend_schema(tags=["Cloth Types"])
class ClothTypeListCreateView(generics.ListCreateAPIView):
    queryset = ClothType.objects.all().order_by("name")
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Cloth Types"])
class ClothTypeClothOnlyView(APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_carpet=False)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeStartsWithView(APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, letter, format=None):
        queryset = ClothType.objects.filter(name__istartswith=letter, is_carpet=False)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypePinnedView(APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_pinned=True, is_carpet=False)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetOnlyView(APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_carpet=True)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetStartsWithView(APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, letter, format=None):
        queryset = ClothType.objects.filter(name__istartswith=letter, is_carpet=True)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeCarpetPinnedView(APIView):
    serializer_class = ClothTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_pinned=True, is_carpet=True)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypeRetrieveView(generics.RetrieveAPIView):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Cloth Types"])
class ClothTypeUpdateView(generics.UpdateAPIView):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Cloth Types"])
class ClothTypeDeleteView(generics.DestroyAPIView):
    queryset = ClothType.objects.all()
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# service type views
@extend_schema(tags=["Service Types"])
class ServiceTypeListCreateView(generics.ListCreateAPIView):
    queryset = ServiceType.objects.all().order_by("name")
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Service Types"])
class ServiceTypeDetailView(generics.RetrieveAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Service Types"])
class ServiceTypeUpdateView(generics.UpdateAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Service Types"])
class ServiceTypeDeleteView(generics.DestroyAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# handling type views
@extend_schema(tags=["Handling Types"])
class HandlingTypeListCreateView(generics.ListCreateAPIView):
    queryset = HandlingType.objects.all().order_by("name")
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Handling Types"])
class HandlingTypeDetailView(generics.RetrieveAPIView):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Handling Types"])
class HandlingTypeUpdateView(generics.UpdateAPIView):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Handling Types"])
class HandlingTypeDeleteView(generics.DestroyAPIView):
    queryset = HandlingType.objects.all()
    serializer_class = HandlingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# delivery type views
@extend_schema(tags=["Delivery Types"])
class DeliveryTypeListCreateView(generics.ListCreateAPIView):
    queryset = DeliveryType.objects.all().order_by("name")
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeDetailView(generics.RetrieveAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeUpdateView(generics.UpdateAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Delivery Types"])
class DeliveryTypeDeleteView(generics.DestroyAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
