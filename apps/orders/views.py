# core imports
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce

# package imports
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry mixin imports
from apps.organizations.mixins import OrgBranchQuerysetMixin

# laundry model imports
from .models import Order, OrderItem, OrderPayment
from apps.organizations.models import Branch

# laundry permission validator
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

# laundry serializer imports
from apps.customers.models import Customer
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    OrderItemSerializer,
    OrderPaymentSerializer,
    UnpaidCreditOrderSerializer,
)


# Create your views here.
# order views
@extend_schema(tags=["Orders"])
class OrderListCreateView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_order",
        "POST": "orders.add_order",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("-created_at")


@extend_schema(tags=["Orders"])
class OrderRetrieveUpdateDestroyView(
    PermissionRequiredMixin,
    OrgBranchQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_order",
        "PUT": "orders.change_order",
        "PATCH": "orders.change_order",
        "DELETE": "orders.delete_order",
    }

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderDetailSerializer
        return OrderSerializer


@extend_schema(tags=["Orders"])
class OrdersByCustomerView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customer",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.kwargs.get("customer_id")
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise NotFound("Customer not found")

        return qs.filter(customer__id=customer_id).order_by("-created_at")


@extend_schema(tags=["Orders"])
class OrdersByOrganizationView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            Q(organization__parent__isnull=True) | Q(organization__parent__exact=None)
        ).order_by("-created_at")


@extend_schema(tags=["Orders"])
class OrdersByBranchView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.kwargs.get("branch_id")
        try:
            Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            raise NotFound("Branch not found")

        return qs.filter(branches__id=branch_id).order_by("-created_at")


@extend_schema(tags=["Orders"])
class OrdersWithUnpaidCreditView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Order.objects.all()
    serializer_class = UnpaidCreditOrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_order",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.with_unpaid_credit().order_by("-created_at")


@extend_schema(tags=["Orders"])
class OrdersWithUnpaidCreditByCustomerView(
    PermissionRequiredMixin, OrgBranchQuerysetMixin, generics.ListAPIView
):
    queryset = Order.objects.all()
    serializer_class = UnpaidCreditOrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": ["orders.view_order", "customers.view_customer"],
    }

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_id")
        return (
            Order.objects.with_unpaid_credit()
            .filter(customer_id=customer_id)
            .order_by("-created_at")
        )


# order item views
@extend_schema(tags=["Order Items"])
class OrderItemListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = OrderItem.objects.all().order_by("-created_at")
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_orderitem",
        "POST": "orders.add_orderitem",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Order Items"])
class OrderItemRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_orderitem",
        "PUT": "orders.change_orderitem",
        "PATCH": "orders.change_orderitem",
        "DELETE": "orders.delete_orderitem",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Order Payments"])
class OrderPaymentListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = OrderPayment.objects.all().order_by("-created_at")
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_orderpayment",
        "POST": "orders.add_orderpayment",
    }


@extend_schema(tags=["Order Payments"])
class OrderPaymentRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = OrderPayment.objects.all()
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_orderpayment",
        "PUT": "orders.change_orderpayment",
        "PATCH": "orders.change_orderpayment",
        "DELETE": "orders.delete_orderpayment",
    }


@extend_schema(tags=["Order Payments"])
class OrderPaymentsByOrderView(PermissionRequiredMixin, generics.ListAPIView):
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": ["orders.view_orderpayment", "orders.view_order"],
    }

    def get_queryset(self):
        order_id = self.kwargs.get("order_id")
        try:
            Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("Order not found")

        return OrderPayment.objects.filter(order__id=order_id).order_by("-created_at")


@extend_schema(tags=["Order Payments"])
class OrderPaymentsByCustomerView(PermissionRequiredMixin, generics.ListAPIView):
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "customers.view_customer",
    }

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_id")
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise NotFound("Customer not found")

        return OrderPayment.objects.filter(order__customer__id=customer_id).order_by(
            "-created_at"
        )
