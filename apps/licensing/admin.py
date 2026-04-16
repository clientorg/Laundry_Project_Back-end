from django.contrib import admin
from .models import AppliedLicense


@admin.register(AppliedLicense)
class AppliedLicenseAdmin(admin.ModelAdmin):
    list_display = (
        "license_id",
        "company_name",
        "organization",
        "plan_name",
        "expires_on",
        "is_active",
        "applied_at",
    )

    list_filter = (
        "is_active",
        "plan_name",
        "expires_on",
    )

    search_fields = (
        "license_id",
        "company_name",
        "organization__name",
        "plan_name",
    )

    readonly_fields = (
        "license_id",
        "organization",
        "company_name",
        "plan_name",
        "raw_key",
        "expires_on",
        "applied_at",
        "created_at",
    )

    ordering = ("-id",)
