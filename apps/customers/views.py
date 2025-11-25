from django.shortcuts import render

# package imports
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry mixin imports
from apps.organizations.mixins import OrgBranchQuerysetMixin

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
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = CustomerCategory.objects.all()
    serializer_class = CustomerCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customercategory",
        "POST": "customers.add_customercategory",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("name")


@extend_schema(tags=["Customer Categories"])
class CustomerCategoryRetrieveUpdateDestroyView(
    PermissionRequiredMixin,
    OrgBranchQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
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


# customer views
@extend_schema(tags=["Customers"])
class CustomerListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": ["customers.view_customer", "orders.add_order"],
        "POST": ["customers.add_customer", "orders.add_order"],
    }

    def get_queryset(self):
        return super().get_queryset().order_by("-created_at")


@extend_schema(tags=["Customers"])
class CustomerRetrieveUpdateDestroyView(
    PermissionRequiredMixin,
    OrgBranchQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
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

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()

        if customer.orders.exists():
            return Response(
                {"detail": "Cannot delete customer with existing orders."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Customer Categories"])
class CategoryCustomerListView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    """
    List customers that belong to a specific CustomerCategory (by category PK).
    URL: /api/customers/categories/<pk>/customers/
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customer",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.kwargs.get("pk")
        if category_id is None:
            return qs.none()
        return qs.filter(category__id=category_id).order_by("-created_at")
