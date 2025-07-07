from django.contrib import admin

# laundry model imports
from .models import Order, OrderItem
from apps.organizations.models import Organization


# Register your models here.
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "cloth_name",
        "service_name",
        "quantity",
        "price",
        "vat_price",
        "total",
        "order",
        "created_by",
        "created_at",
    )
    search_fields = ("cloth_name", "service_name")
    list_filter = ("created_at", "order", "cloth_name", "service_name")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (
            "",
            {
                "fields": (
                    "order",
                    "cloth_name",
                    "cloth_arabic_name",
                    "cloth_description",
                    "cloth_price",
                    "service_name",
                    "service_description",
                    "service_price",
                    "handling_name",
                    "handling_description",
                    "handling_price",
                    "delivery_name",
                    "delivery_description",
                    "delivery_charge_percent",
                    "delivery_charge_price",
                    "customer_category_name",
                    "customer_category_discount_percent",
                    "customer_category_discount_price",
                    "length",
                    "width",
                    "area",
                    "rate_per_area",
                    "area_price",
                    "quantity",
                    "price",
                    "vat_percent",
                    "vat_price",
                    "total",
                )
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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "customer",
        "status",
        "price",
        "discount_price",
        "vat_price",
        "total",
        "inward_date",
        "delivery_date",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "created_at", "delivery_date")
    search_fields = ("order_id", "customer__name", "status")
    readonly_fields = ("inward_date", "created_at", "updated_at", "order_id")

    fieldsets = (
        (
            "Order Details",
            {
                "fields": (
                    "order_id",
                    "status",
                    "data",
                    "customer",
                    "organization",
                    "branches",
                    "delivery_date",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "delivery_charge_percent",
                    "delivery_charge_price",
                    "discount_percent",
                    "discount_price",
                    "vat_percent",
                    "vat_price",
                    "price",
                    "total",
                )
            },
        ),
        (
            "Meta",
            {
                "fields": (
                    "inward_date",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                )
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
