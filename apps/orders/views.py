from django.shortcuts import render

# package imports
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# laundry model imports
from .models import Order, OrderItem, OrderPayment

# laundry serializer imports
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    OrderItemSerializer,
    OrderPaymentSerializer,
    OrderPaymentInlineSerializer,
)


# Create your views here.
# order views
@extend_schema(tags=["Orders"])
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


@extend_schema(tags=["Orders"])
class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderDetailSerializer
        return OrderSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


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
