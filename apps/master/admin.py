from django.contrib import admin
from django.utils.html import format_html

# Laundry Models
from apps.organizations.models import Organization
from .models import Country, Item, ClothType, ServiceType, HandlingType, DeliveryType


# Register your models here.
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "flag_emoji", "iso_code", "dial_code")
    search_fields = ("name", "iso_code", "dial_code")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = (
        "is_global",
        "is_active",
        "is_pinned",
        "is_size_based_price",
        "is_laundry",
        "is_pressing",
        "is_dry_clean",
        "is_steam",
    )
    search_fields = (
        "name",
        "secondary_name",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "secondary_name",
        "organization",
        "branches_count",
        "is_active",
        "is_global",
        "is_pinned",
        "is_size_based_price",
        "image_tag",
        "created_at",
        "updated_at",
    )

    # form config
    readonly_fields = [
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "image_tag",
    ]
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "name",
                    "secondary_name",
                    "description",
                    "is_active",
                    "is_global",
                    "is_pinned",
                    "is_size_based_price",
                    "is_laundry",
                    "laundry_price",
                    "is_pressing",
                    "pressing_price",
                    "is_dry_clean",
                    "dry_clean_price",
                    "is_steam",
                    "steam_price",
                    "image",
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
    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "-"

    image_tag.short_description = "Image"

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


@admin.register(ClothType)
class ClothTypeAdmin(admin.ModelAdmin):
    # table config
    filter_horizontal = ("branches",)
    list_filter = (
        "is_global",
        "is_active",
        "is_pinned",
        "is_carpet",
    )
    search_fields = (
        "name",
        "arabic_name",
        "organization__name",
        "created_by__username",
        "updated_by__username",
    )
    list_display = (
        "name",
        "arabic_name",
        "price",
        "organization",
        "branches_count",
        "is_global",
        "is_active",
        "is_pinned",
        "is_carpet",
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
                    "arabic_name",
                    "description",
                    "price",
                    "is_active",
                    "is_global",
                    "is_pinned",
                    "is_carpet",
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


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
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


@admin.register(HandlingType)
class HandlingTypeAdmin(admin.ModelAdmin):
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
        "charge_percent",
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
                    "charge_percent",
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
