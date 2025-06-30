from django.shortcuts import render

# package imports
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# master model imports
from .models import ClothType, ServiceType, HandlingType, DeliveryType

# master serializer imports
from .serializers import (
    ClothTypeSerializer,
    ServiceTypeSerializer,
    HandlingTypeSerializer,
    DeliveryTypeSerializer,
)


# Create your views here.
# cloth types api
@extend_schema(tags=["Cloth Types"])
class ClothTypeListCreateView(generics.ListCreateAPIView):
    queryset = ClothType.objects.all().order_by("name")
    serializer_class = ClothTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Cloth Types"])
class ClothTypeStartsWithView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, letter, format=None):
        queryset = ClothType.objects.filter(name__istartswith=letter)
        serializer = ClothTypeSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Cloth Types"])
class ClothTypePinnedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        queryset = ClothType.objects.filter(is_pinned=True)
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


# washing types api
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


# handling types api
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


# delivery types api
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
