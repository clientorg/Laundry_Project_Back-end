from django.urls import path
from .views import (
    # order views
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView,
    # order item views
    OrderItemListCreateView,
    OrderItemRetrieveUpdateDestroyView,
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
]
