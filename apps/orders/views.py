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
            organization__isnull=False, organization__parent__isnull=True
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

        # if 'all' → return all branches’ orders
        if branch_id == "all":
            return qs.filter(organization__isnull=True).order_by("-created_at")

        # otherwise, validate numeric branch id
        try:
            branch_id = int(branch_id)
        except ValueError:
            raise NotFound("Invalid branch ID")

        if not Branch.objects.filter(id=branch_id).exists():
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


# ---------------------------- Mark Order as Ready and send WhatsApp notification   ----------------------------  
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.whatsapp import send_whatsapp_template
from rest_framework.exceptions import NotFound
from django.conf import settings

@extend_schema(
    tags=["Orders"],
    summary="Mark order as ready and send WhatsApp notification",
    description="Updates order status to READY and sends WhatsApp template message.",
)
class MarkOrderReadyView(APIView):
    def post(self, request, order_id):
        from .models import Order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("Order not found")

        # Update status
        order.status = "READY"
        order.save()

        # Send WhatsApp Message
        phone = f"{order.customer.country_code}{order.customer.mobile_number}"

        send_whatsapp_template(
            to=phone,
            template_name="hello_world",   # your test template
            params=[]                      # hello_world has no parameters
        )

        return Response(
            {"message": "Order ready & WhatsApp notification sent"},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Orders"],
    summary="Mark order as delivered and send WhatsApp notification",
    description="Updates order status to DELIVERED and sends WhatsApp notification to customer.",
)
class MarkOrderDeliveredView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        from .models import Order
        from .services.whatsapp import notify_order_delivered
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("Order not found")

        order.status = "DELIVERED"
        order.save()

        result = notify_order_delivered(order)
        return Response(
            {"message": "Order delivered & WhatsApp notification sent", "whatsapp": result},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Orders"],
    summary="Send custom WhatsApp message to customer",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number with country code"},
                "message": {"type": "string", "description": "Free-form text message"},
            },
            "required": ["phone", "message"],
        }
    },
)
class SendCustomWhatsAppView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .services.whatsapp import send_custom_text
        phone = request.data.get("phone")
        message = request.data.get("message")
        if not phone or not message:
            return Response(
                {"error": "Both 'phone' and 'message' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = send_custom_text(to=phone, message=message)
        return Response({"message": "WhatsApp message sent", "whatsapp": result}, status=status.HTTP_200_OK)


# ---------------------------- WhatsApp: Order Placement ----------------------------

@extend_schema(
    tags=["WhatsApp"],
    summary="Send WhatsApp notification for order placement",
    description="Sends an order placement confirmation message to the customer via WhatsApp.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "customer_name":  {"type": "string", "description": "Customer full name"},
                "phone":          {"type": "string", "description": "Phone number with country code (e.g. 96599123456)"},
                "voucher_number": {"type": "string", "description": "Order voucher/reference number"},
                "status":         {"type": "string", "description": "Current order status"},
            },
            "required": ["customer_name", "phone", "voucher_number", "status"],
        }
    },
)
class SendOrderPlacementWhatsAppView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .services.whatsapp import notify_order_placement
        customer_name  = request.data.get("customer_name")
        phone          = request.data.get("phone")
        voucher_number = request.data.get("voucher_number")
        order_status   = request.data.get("status")

        if not all([customer_name, phone, voucher_number, order_status]):
            return Response(
                {"error": "customer_name, phone, voucher_number and status are all required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = notify_order_placement(customer_name, phone, voucher_number, order_status)
        return Response(
            {"message": "Order placement WhatsApp notification sent", "whatsapp": result},
            status=status.HTTP_200_OK,
        )


# ---------------------------- WhatsApp: Order Status Update ----------------------------

@extend_schema(
    tags=["WhatsApp"],
    summary="Send WhatsApp notification for order status update",
    description="Sends an order status update message to the customer via WhatsApp.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "customer_name":  {"type": "string", "description": "Customer full name"},
                "phone":          {"type": "string", "description": "Phone number with country code (e.g. 96599123456)"},
                "voucher_number": {"type": "string", "description": "Order voucher/reference number"},
                "status":         {"type": "string", "description": "Updated order status"},
            },
            "required": ["customer_name", "phone", "voucher_number", "status"],
        }
    },
)
class SendOrderStatusUpdateWhatsAppView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .services.whatsapp import notify_order_status_update
        customer_name  = request.data.get("customer_name")
        phone          = request.data.get("phone")
        voucher_number = request.data.get("voucher_number")
        order_status   = request.data.get("status")

        if not all([customer_name, phone, voucher_number, order_status]):
            return Response(
                {"error": "customer_name, phone, voucher_number and status are all required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = notify_order_status_update(customer_name, phone, voucher_number, order_status)
        return Response(
            {"message": "Order status update WhatsApp notification sent", "whatsapp": result},
            status=status.HTTP_200_OK,
        )
