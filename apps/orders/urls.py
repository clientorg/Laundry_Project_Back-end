from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDeleteView,
    OrderByUserView,
    OrderUpdateView,
)

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("<int:pk>/", OrderDeleteView.as_view(), name="order-delete"),
    path("user/<int:user_id>/", OrderByUserView.as_view(), name="orders-by-user"),
    path("<int:pk>/edit/", OrderUpdateView.as_view(), name="order-update"),
]
