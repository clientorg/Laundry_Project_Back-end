from django.contrib import admin

# Laundry Models
from .models import ClothType, WashingType, DeliveryType
from apps.organizations.models import Organization


# Register your models here.
@admin.register(ClothType)
class ClothTypeAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = ("is_global", "is_active", "is_pinned")
    search_fields = (
        "name",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "price",
        "organization",
        "branches_count",
        "is_global",
        "is_active",
        "is_pinned",
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
                    "price",
                    "is_active",
                    "is_global",
                    "is_pinned",
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


@admin.register(WashingType)
class WashingTypeAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = ("is_global", "is_active", "is_pinned")
    search_fields = (
        "name",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "price",
        "organization",
        "branches_count",
        "is_global",
        "is_active",
        "is_pinned",
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
                    "price",
                    "is_active",
                    "is_global",
                    "is_pinned",
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


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = ("is_global", "is_active", "is_pinned")
    search_fields = (
        "name",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "price",
        "organization",
        "branches_count",
        "is_global",
        "is_active",
        "is_pinned",
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
                    "price",
                    "is_active",
                    "is_global",
                    "is_pinned",
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
