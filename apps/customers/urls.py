from django.urls import path
from .views import (
    CustomerListCreateView,
    CustomerDeleteView,
    CustomerByUserView,
    CustomerUpdateView,
)

urlpatterns = [
    path("", CustomerListCreateView.as_view(), name="customer-list-create"),
    path("<int:pk>/", CustomerDeleteView.as_view(), name="customer-delete"),
    path("user/<int:user_id>/", CustomerByUserView.as_view(), name="customers-by-user"),
    path("<int:pk>/edit/", CustomerUpdateView.as_view(), name="customer-update"),
]
