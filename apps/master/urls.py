from django.urls import path

# master view imports
from .views import (
    # cloth type views
    ClothTypeListCreateView,
    ClothTypeStartsWithView,
    ClothTypePinnedView,
    ClothTypeRetrieveView,
    ClothTypeUpdateView,
    ClothTypeDeleteView,
    # washing type views
    ServiceTypeListCreateView,
    ServiceTypeDetailView,
    ServiceTypeUpdateView,
    ServiceTypeDeleteView,
    # handling type views
    HandlingTypeListCreateView,
    HandlingTypeDetailView,
    HandlingTypeUpdateView,
    HandlingTypeDeleteView,
    # delivery type views
    DeliveryTypeListCreateView,
    DeliveryTypeDetailView,
    DeliveryTypeUpdateView,
    DeliveryTypeDeleteView,
)

# urls.py
urlpatterns = [
    # cloth type urls
    path(
        "cloth-types/", ClothTypeListCreateView.as_view(), name="cloth-type-list-create"
    ),
    path(
        "cloth-types/starts-with/<str:letter>/",
        ClothTypeStartsWithView.as_view(),
        name="cloth-types-starts-with",
    ),
    path(
        "cloth-types/pinned/",
        ClothTypePinnedView.as_view(),
        name="cloth-type-pinned",
    ),
    path(
        "cloth-types/<int:pk>/",
        ClothTypeRetrieveView.as_view(),
        name="cloth-type-detail",
    ),
    path(
        "cloth-types/<int:pk>/update/",
        ClothTypeUpdateView.as_view(),
        name="cloth-type-update",
    ),
    path(
        "cloth-types/<int:pk>/delete/",
        ClothTypeDeleteView.as_view(),
        name="cloth-type-delete",
    ),
    # washing type urls
    path(
        "service-types/",
        ServiceTypeListCreateView.as_view(),
        name="service-type-list-create",
    ),
    path(
        "service-types/<int:pk>/",
        ServiceTypeDetailView.as_view(),
        name="service-type-detail",
    ),
    path(
        "service-types/<int:pk>/update/",
        ServiceTypeUpdateView.as_view(),
        name="service-type-update",
    ),
    path(
        "service-types/<int:pk>/delete/",
        ServiceTypeDeleteView.as_view(),
        name="service-type-delete",
    ),
    # handling type urls
    path(
        "handling-types/",
        HandlingTypeListCreateView.as_view(),
        name="handling-type-list-create",
    ),
    path(
        "handling-types/<int:pk>/",
        HandlingTypeDetailView.as_view(),
        name="handling-type-detail",
    ),
    path(
        "handling-types/<int:pk>/update/",
        HandlingTypeUpdateView.as_view(),
        name="handling-type-update",
    ),
    path(
        "handling-types/<int:pk>/delete/",
        HandlingTypeDeleteView.as_view(),
        name="handling-type-delete",
    ),
    # delivery type urls
    path(
        "delivery-types/",
        DeliveryTypeListCreateView.as_view(),
        name="delivery-type-list-create",
    ),
    path(
        "delivery-types/<int:pk>/",
        DeliveryTypeDetailView.as_view(),
        name="delivery-type-detail",
    ),
    path(
        "delivery-types/<int:pk>/update/",
        DeliveryTypeUpdateView.as_view(),
        name="delivery-type-update",
    ),
    path(
        "delivery-types/<int:pk>/delete/",
        DeliveryTypeDeleteView.as_view(),
        name="delivery-type-delete",
    ),
]
