from django.urls import path

# laundry view imports
from .views import (
    # customer category views
    CustomerCategoryListCreateView,
    CustomerCategoryRetrieveUpdateDestroyView,
    # customer views
    CustomerListCreateView,
    CustomerRetrieveUpdateDestroyView,
)

urlpatterns = [
    # customer category urls
    path(
        "customer-categories/",
        CustomerCategoryListCreateView.as_view(),
        name="customer-category-list-create",
    ),
    path(
        "customer-categories/<int:pk>/",
        CustomerCategoryRetrieveUpdateDestroyView.as_view(),
        name="customer-category-detail",
    ),
    # customer urls
    path(
        "",
        CustomerListCreateView.as_view(),
        name="customer-list-create",
    ),
    path(
        "<int:pk>/",
        CustomerRetrieveUpdateDestroyView.as_view(),
        name="customer-detail",
    ),
]
