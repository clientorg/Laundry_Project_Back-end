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
    WashingTypeListCreateView,
    WashingTypeDetailView,
    WashingTypeUpdateView,
    WashingTypeDeleteView,
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
        "washing-types/",
        WashingTypeListCreateView.as_view(),
        name="washing-type-list-create",
    ),
    path(
        "washing-types/<int:pk>/",
        WashingTypeDetailView.as_view(),
        name="washing-type-detail",
    ),
    path(
        "washing-types/<int:pk>/update/",
        WashingTypeUpdateView.as_view(),
        name="washing-type-update",
    ),
    path(
        "washing-types/<int:pk>/delete/",
        WashingTypeDeleteView.as_view(),
        name="washing-type-delete",
    ),
]
