# core imports
from rest_framework.exceptions import NotFound

# package imports
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry model imports
from .models import Order, OrderItem, OrderPayment

# laundry permission validator
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

# laundry serializer imports
from apps.customers.models import Customer
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    OrderItemSerializer,
    OrderPaymentSerializer,
)


# Create your views here.
# order views
@extend_schema(tags=["Orders"])
class OrderListCreateView(PermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "orders.view_order",
        "POST": "orders.add_order",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Orders"])
class OrderRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Orders"])
class OrdersByCustomerView(PermissionRequiredMixin, generics.ListAPIView):
    serializer_class = OrderSerializer
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

        return Order.objects.filter(customer__id=customer_id).order_by("-created_at")


# order item views
@extend_schema(tags=["Order Items"])
class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all().order_by("-created_at")
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Order Items"])
class OrderItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=["Order Payments"])
class OrderPaymentListCreateView(generics.ListCreateAPIView):
    queryset = OrderPayment.objects.all().order_by("-created_at")
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Order Payments"])
class OrderPaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderPayment.objects.all()
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Order Payments"])
class OrderPaymentsByCustomerView(generics.ListAPIView):
    serializer_class = OrderPaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_id")
        return OrderPayment.objects.filter(order__customer__id=customer_id).order_by(
            "-created_at"
        )
