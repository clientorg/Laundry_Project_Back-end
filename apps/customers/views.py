from django.shortcuts import render

# package imports
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry model imports
from .models import CustomerCategory, Customer

# laundry serializer imports
from .serializers import CustomerCategorySerializer, CustomerSerializer


# Create your views here.
# customer category views
@extend_schema(tags=["Customer Categories"])
class CustomerCategoryListCreateView(generics.ListCreateAPIView):
    queryset = CustomerCategory.objects.all().order_by("name")
    serializer_class = CustomerCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Customer Categories"])
class CustomerCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerCategory.objects.all()
    serializer_class = CustomerCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# customer views
@extend_schema(tags=["Customers"])
class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Customers"])
class CustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
