from django.urls import path
from .views import (
    DashboardKPIView,
    PnLReportView,
    CustomerListReportView,
    UnpaidCustomersReportView,
)

urlpatterns = [
    path("dashboard/", DashboardKPIView.as_view(), name="dashboard-kpi"),
    path("pnl/", PnLReportView.as_view(), name="pnl-report"),
    path("customers/", CustomerListReportView.as_view(), name="customer-list-report"),
    path("unpaid-customers/", UnpaidCustomersReportView.as_view(), name="unpaid-customers-report"),
]
