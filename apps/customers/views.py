from django.shortcuts import render

# package imports
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry permission validator
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

# laundry model imports
from .models import CustomerCategory, Customer

# laundry serializer imports
from .serializers import CustomerCategorySerializer, CustomerSerializer


# Create your views here.
# customer category views
@extend_schema(tags=["Customer Categories"])
class CustomerCategoryListCreateView(
    PermissionRequiredMixin, generics.ListCreateAPIView
):
    queryset = CustomerCategory.objects.all().order_by("name")
    serializer_class = CustomerCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customercategory",
        "POST": "customers.add_customercategory",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Customer Categories"])
class CustomerCategoryRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = CustomerCategory.objects.all()
    serializer_class = CustomerCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customercategory",
        "PUT": "customers.change_customercategory",
        "PATCH": "customers.change_customercategory",
        "DELETE": "customers.delete_customercategory",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# customer views
@extend_schema(tags=["Customers"])
class CustomerListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": ["customers.view_customer", "orders.add_order"],
        "POST": ["customers.add_customer", "orders.add_order"],
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Customers"])
class CustomerRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customer",
        "PUT": "customers.change_customer",
        "PATCH": "customers.change_customer",
        "DELETE": "customers.delete_customer",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()

        if customer.orders.exists():
            return Response(
                {"detail": "Cannot delete customer with existing orders."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)
