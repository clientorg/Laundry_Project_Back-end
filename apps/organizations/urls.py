# core imports
from django.urls import path

# laundry view imports
from .views import (
    BranchListCreateView, 
    BranchRetrieveUpdateDestroyView,
    OrganizationListCreateView,
    OrganizationRetrieveUpdateDestroyView,
)


# urls.py
urlpatterns = [
    path("branches/", BranchListCreateView.as_view(), name="branch-list-create"),
    path(
        "branches/<int:pk>/",
        BranchRetrieveUpdateDestroyView.as_view(),
        name="branch-detail",
    ),
    path("organizations/", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path("organizations/<int:pk>/", OrganizationRetrieveUpdateDestroyView.as_view(), name="organization-detail"),
]
