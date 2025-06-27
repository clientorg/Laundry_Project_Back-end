from django.shortcuts import render

# package imports
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# master model imports
from .models import ClothType, WashingType

# master serializer imports
from .serializers import ClothTypeSerializer, WashingTypeSerializer


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
@extend_schema(tags=["Washing Types"])
class WashingTypeListCreateView(generics.ListCreateAPIView):
    queryset = WashingType.objects.all().order_by("name")
    serializer_class = WashingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Washing Types"])
class WashingTypeDetailView(generics.RetrieveAPIView):
    queryset = WashingType.objects.all()
    serializer_class = WashingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Washing Types"])
class WashingTypeUpdateView(generics.UpdateAPIView):
    queryset = WashingType.objects.all()
    serializer_class = WashingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Washing Types"])
class WashingTypeDeleteView(generics.DestroyAPIView):
    queryset = WashingType.objects.all()
    serializer_class = WashingTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
