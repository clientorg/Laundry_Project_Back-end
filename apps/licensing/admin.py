from django.contrib import admin
from .models import AppliedLicense, License
from .service import generate_license_key
from datetime import date, timedelta


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


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        "license_id",
        "license_type",
        "company_name",
        "plan_name",
        "price",
        "duration_days",
        "expires_on",
        "created_by",
        "created_at",
    )

    list_filter = (
        "license_type",
        "plan_name",
        "expires_on",
    )

    search_fields = (
        "license_id",
        "company_name",
        "plan_name",
        "admin_username",
        "admin_email",
    )

    readonly_fields = (
        "license_key",
        "duration_days",
        "expires_on",
        "created_at",
        "updated_at",
        "created_by",
    )

    fieldsets = (
        (
            "License",
            {
                "fields": (
                    "license_id",
                    "license_type",
                    "company_name",
                    "plan_name",
                    "price",
                    "max_branches",
                    "max_users",
                    "duration_days",
                    "expires_on",
                )
            },
        ),
        (
            "Activation Admin",
            {
                "fields": (
                    "admin_username",
                    "admin_name",
                    "admin_email",
                    "admin_password",
                )
            },
        ),
        (
            "Generated License Key",
            {
                "fields": ("license_key",),
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.expires_on = date.today() + timedelta(days=obj.duration_days)
            obj.license_key = generate_license_key(obj)

        super().save_model(request, obj, form, change)
