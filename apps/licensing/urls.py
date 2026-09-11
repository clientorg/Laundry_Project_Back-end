from django.urls import path
from .views import LicenseStatusView, ApplyLicenseView, LicenseListCreateView

urlpatterns = [
    path(
        "status/",
        LicenseStatusView.as_view(),
        name="license-status",
    ),
    path(
        "apply/",
        ApplyLicenseView.as_view(),
        name="license-apply",
    ),
    path(
        "licenses/",
        LicenseListCreateView.as_view(),
        name="license-list-create",
    ),
]
