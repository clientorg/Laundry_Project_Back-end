from django.urls import path
from .views import (
    # order views
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView,
    OrdersByCustomerView,
    # order item views
    OrderItemListCreateView,
    OrderItemRetrieveUpdateDestroyView,
    # order payment views
    OrderPaymentListCreateView,
    OrderPaymentRetrieveUpdateDestroyView,
    OrderPaymentsByCustomerView,
)

urlpatterns = [
    # order URLs
    path(
        "orders/",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),
    path(
        "orders/<int:pk>/",
        OrderRetrieveUpdateDestroyView.as_view(),
        name="order-detail",
    ),
    path(
        "orders/by-customer/<int:customer_id>/",
        OrdersByCustomerView.as_view(),
        name="orders-by-customer",
    ),
    # order item URLs
    path(
        "order-items/",
        OrderItemListCreateView.as_view(),
        name="orderitem-list-create",
    ),
    path(
        "order-items/<int:pk>/",
        OrderItemRetrieveUpdateDestroyView.as_view(),
        name="orderitem-detail",
    ),
    # order payment URLs
    path(
        "order-payments/",
        OrderPaymentListCreateView.as_view(),
        name="order-payment-list-create",
    ),
    path(
        "order-payments/<int:pk>/",
        OrderPaymentRetrieveUpdateDestroyView.as_view(),
        name="order-payment-detail",
    ),
    path(
        "order-payments/by-customer/<int:customer_id>/",
        OrderPaymentsByCustomerView.as_view(),
        name="payments-by-customer",
    ),
]
