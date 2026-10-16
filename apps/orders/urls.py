from django.urls import path
from .views import (
    # order views
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView,
    OrdersByCustomerView,
    OrdersByOrganizationView,
    OrdersByBranchView,
    OrdersWithUnpaidCreditView,
    OrdersWithUnpaidCreditByCustomerView,
    # order item views
    OrderItemListCreateView,
    OrderItemRetrieveUpdateDestroyView,
    # order payment views
    OrderPaymentListCreateView,
    OrderPaymentRetrieveUpdateDestroyView,
    OrderPaymentsByOrderView,
    OrderPaymentsByCustomerView,
    # WhatsApp / status actions
    MarkOrderReadyView,
    MarkOrderDeliveredView,
    SendCustomWhatsAppView,
    SendOrderPlacementWhatsAppView,
    SendOrderStatusUpdateWhatsAppView,
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
    path(
        "orders/by-organization/",
        OrdersByOrganizationView.as_view(),
        name="orders-by-organization",
    ),
    path(
        "orders/by-branch/<str:branch_id>/",
        OrdersByBranchView.as_view(),
        name="orders-by-branch",
    ),
    path(
        "orders/unpaid-credit/",
        OrdersWithUnpaidCreditView.as_view(),
        name="orders-unpaid-credit",
    ),
    path(
        "orders/unpaid-credit/by-customer/<int:customer_id>/",
        OrdersWithUnpaidCreditByCustomerView.as_view(),
        name="orders-unpaid-credit-by-customer",
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
        "order-payments/by-order/<int:order_id>/",
        OrderPaymentsByOrderView.as_view(),
        name="payments-by-order",
    ),
    path(
        "order-payments/by-customer/<int:customer_id>/",
        OrderPaymentsByCustomerView.as_view(),
        name="payments-by-customer",
    ),
    # custom action to mark order as ready
    path("orders/<int:order_id>/mark-ready/", MarkOrderReadyView.as_view(), name="order-mark-ready"),
    # custom action to mark order as delivered
    path("orders/<int:order_id>/mark-delivered/", MarkOrderDeliveredView.as_view(), name="order-mark-delivered"),
    # send custom WhatsApp message
    path("whatsapp/send/", SendCustomWhatsAppView.as_view(), name="whatsapp-send-custom"),
    # order placement WhatsApp notification
    path("whatsapp/order-placement/", SendOrderPlacementWhatsAppView.as_view(), name="whatsapp-order-placement"),
    # order status update WhatsApp notification
    path("whatsapp/order-status-update/", SendOrderStatusUpdateWhatsAppView.as_view(), name="whatsapp-order-status-update"),
]
