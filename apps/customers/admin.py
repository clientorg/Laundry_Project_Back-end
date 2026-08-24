from django.contrib import admin

# Laundry Models
from .models import Customer, CustomerCategory
from apps.organizations.models import Organization


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = ("is_active",)
    search_fields = (
        "name",
        "tax_number",
        "email",
        "country_code",
        "mobile_number",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "tax_number",
        "email",
        "mobile_no",
        "credit_limit",
        "opening_due",
        "credit_used",
        "credit_remaining",
        "category",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
    )

    # form config
    readonly_fields = [
        "customer_id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "name",
                    "tax_number",
                    "email",
                    "address",
                    "country_code",
                    "mobile_number",
                    "credit_limit",
                    "opening_due",
                    "category",
                    "is_active",
                ),
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": ("organization", "branches"),
            },
        ),
        (
            "Meta",
            {
                "fields": (
                    "customer_id",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    # custom fields
    def mobile_no(self, obj):
        return f"{obj.country_code} {obj.mobile_number}"

    def credit_used(self, obj):
        return obj.credit_used()

    def credit_remaining(self, obj):
        return obj.credit_remaining()

    def branches_count(self, obj):
        return obj.branches.count()

    # relation config
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # action config
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(CustomerCategory)
class CustomerCategoryAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = ("is_active", "is_global")
    search_fields = (
        "name",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "discount_percent",
        "organization",
        "branches_count",
        "is_global",
        "is_active",
        "created_by",
        "updated_by",
    )

    # form config
    readonly_fields = [
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "name",
                    "description",
                    "discount_percent",
                    "is_active",
                    "is_global",
                ),
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": ("organization", "branches"),
            },
        ),
        (
            "Meta",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    # custom fields
    def branches_count(self, obj):
        return obj.branches.count()

    # relation config
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # action config
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)
