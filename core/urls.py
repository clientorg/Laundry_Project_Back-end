"""
URL configuration for LaundryBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # api setup
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/organizations/", include("apps.organizations.urls")),
    path("api/master/", include("apps.master.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/customers/", include("apps.customers.urls")),
    path("api/purchase/", include("apps.purchase.urls")),
    path("api/expenses/", include("apps.expenses.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/license/", include("apps.licensing.urls")),
    # Swagger UI:
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # swagger setup
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Redoc UI:
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
