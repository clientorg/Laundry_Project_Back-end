# core imports
from django.urls import path

# laundry view imports
from .views import BranchListCreateView, BranchRetrieveUpdateDestroyView


# urls.py
urlpatterns = [
    path("branches/", BranchListCreateView.as_view(), name="branch-list-create"),
    path(
        "branches/<int:pk>/",
        BranchRetrieveUpdateDestroyView.as_view(),
        name="branch-detail",
    ),
]
