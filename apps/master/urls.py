from django.urls import path

# laundry view imports
from .views import (
    # master views
    CountryMasterView,
    # item views
    ItemListCreateView,
    ItemRetrieveUpdateDestroyView,
    ItemClothOnlyView,
    ItemClothOnlyPinnedView,
    ItemClothOnlyStartsWithView,
    ItemCarpetOnlyView,
    ItemCarpetOnlyPinnedView,
    ItemCarpetOnlyStartsWithView,
    # cloth type views
    ClothTypeListCreateView,
    ClothTypeClothOnlyView,
    ClothTypeStartsWithView,
    ClothTypePinnedView,
    ClothTypeCarpetOnlyView,
    ClothTypeCarpetStartsWithView,
    ClothTypeCarpetPinnedView,
    ClothTypeRetrieveView,
    ClothTypeUpdateView,
    ClothTypeDeleteView,
    # washing type views
    ServiceTypeListCreateView,
    ServiceTypeListInwardView,
    ServiceTypeDetailView,
    ServiceTypeUpdateView,
    ServiceTypeDeleteView,
    # handling type views
    HandlingTypeListCreateView,
    HandlingTypeListInwardView,
    HandlingTypeDetailView,
    HandlingTypeUpdateView,
    HandlingTypeDeleteView,
    # delivery type views
    DeliveryTypeListCreateView,
    DeliveryTypeListInwardView,
    DeliveryTypeDetailView,
    DeliveryTypeUpdateView,
    DeliveryTypeDeleteView,
)

# urls.py
urlpatterns = [
    # master urls
    path(
        "countries/",
        CountryMasterView.as_view(),
        name="countries-list",
    ),
    # item urls
    path("items/", ItemListCreateView.as_view(), name="item-list-create"),
    path(
        "items/<int:pk>/", ItemRetrieveUpdateDestroyView.as_view(), name="item-detail"
    ),
    path(
        "items/inward/cloth-only/",
        ItemClothOnlyView.as_view(),
        name="item-cloth-only",
    ),
    path(
        "items/inward/cloth-only/pinned/",
        ItemClothOnlyPinnedView.as_view(),
        name="item-cloth-only-pinned",
    ),
    path(
        "items/inward/cloth-only/starts-with/<str:letter>/",
        ItemClothOnlyStartsWithView.as_view(),
        name="item-cloth-only-starts-with",
    ),
    path(
        "item/inward/carpet-only/",
        ItemCarpetOnlyView.as_view(),
        name="item-carpet-only",
    ),
    path(
        "item/inward/carpet-only/pinned/",
        ItemCarpetOnlyPinnedView.as_view(),
        name="item-carpet-only-pinned",
    ),
    path(
        "item/inward/carpet-only/starts-with/<str:letter>/",
        ItemCarpetOnlyStartsWithView.as_view(),
        name="item-carpet-only-starts-with",
    ),
    # cloth type urls
    path(
        "cloth-types/", ClothTypeListCreateView.as_view(), name="cloth-type-list-create"
    ),
    path(
        "cloth-types/inward/cloth-only/",
        ClothTypeClothOnlyView.as_view(),
        name="cloth-type-inward-cloth-only",
    ),
    path(
        "cloth-types/inward/cloth/starts-with/<str:letter>/",
        ClothTypeStartsWithView.as_view(),
        name="cloth-types-inward-starts-with",
    ),
    path(
        "cloth-types/inward/cloth/pinned/",
        ClothTypePinnedView.as_view(),
        name="cloth-type-inward-pinned",
    ),
    path(
        "cloth-types/inward/carpet-only/",
        ClothTypeCarpetOnlyView.as_view(),
        name="cloth-type-inward-carpet-only",
    ),
    path(
        "cloth-types/inward/carpet/starts-with/<str:letter>/",
        ClothTypeCarpetStartsWithView.as_view(),
        name="cloth-types-inward-carpet-starts-with",
    ),
    path(
        "cloth-types/inward/carpet/pinned/",
        ClothTypeCarpetPinnedView.as_view(),
        name="cloth-type-inward-carpet-pinned",
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
        "service-types/inward/list/",
        ServiceTypeListInwardView.as_view(),
        name="service-type-inward-list",
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
        "handling-types/inward/list/",
        HandlingTypeListInwardView.as_view(),
        name="handling-type-inward-list",
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
        "delivery-types/inward/list/",
        DeliveryTypeListInwardView.as_view(),
        name="delivery-type-inward-list",
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
