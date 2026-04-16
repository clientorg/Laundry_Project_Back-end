from django.urls import path
from .views import LicenseStatusView, ApplyLicenseView

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
]
