# core imports
from django.urls import path

# laundry view imports
from .views import (
    BranchListCreateView, 
    BranchRetrieveUpdateDestroyView,
    OrganizationListCreateView,
    OrganizationRetrieveUpdateDestroyView,
    OrganizationChangePlanView,
    PlanListCreateView,
    PlanRetrieveUpdateDestroyView,
)


# urls.py
urlpatterns = [
    path("branches/", BranchListCreateView.as_view(), name="branch-list-create"),
    path(
        "branches/<int:pk>/",
        BranchRetrieveUpdateDestroyView.as_view(),
        name="branch-detail",
    ),
    #--------------- Organization URLs ---------------#
    path("organizations/", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path("organizations/<int:pk>/", OrganizationRetrieveUpdateDestroyView.as_view(), name="organization-detail"),
    path(
        "organizations/<int:pk>/change-plan/",
        OrganizationChangePlanView.as_view(),
        name="organization-change-plan",
    ),

    #--------------- Plan URLs ---------------#
    path("plans/", PlanListCreateView.as_view(), name="plan-list-create"),
    path("plans/<int:pk>/", PlanRetrieveUpdateDestroyView.as_view(), name="plan-detail"),
]
