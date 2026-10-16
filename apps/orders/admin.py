from django.contrib import admin
from django.db.models import Sum, Q

# laundry model imports
from .models import Order, OrderItem, OrderPayment
from apps.organizations.models import Organization


# Register your models here.
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "cloth_name",
        "service_name",
        "quantity",
        "price",
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
                    "cloth_price",
                    "service_name",
                    "service_price",
                    "handling_name",
                    "handling_price",
                    "delivery_name",
                    "delivery_charge_percent",
                    "customer_category_name",
                    "customer_category_discount_percent",
                    "customer_category_discount_price",
                    "remarks",
                    "length",
                    "width",
                    "area",
                    "rate_per_area",
                    "area_price",
                    "quantity",
                    "price",
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


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "payment_type",
        "received_amount",
        "change_return",
        "apply_rounding",
        "rounding_amount",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "order__order_id",
        "payment_type",
        "created_by__username",
        "updated_by__username",
    )
    list_filter = ("payment_type", "apply_rounding")
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
                    "payment_type",
                    "received_amount",
                    "change_return",
                    "apply_rounding",
                    "rounding_amount",
                    "note",
                )
            },
        ),
        (
            "Feedback",
            {
                "fields": (
                    "rating",
                    "rating_link",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
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
        "total",
        "amount_paid",
        "remaining_amount",
        "is_paid",
        "status",
        "inward_date",
        "delivery_date",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_id", "customer__name", "status")
    readonly_fields = (
        "order_id",
        "inward_date",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

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

    def amount_paid(self, obj):
        return (
            obj.payments.exclude(payment_type="credit").aggregate(
                total=Sum("received_amount")
            )["total"]
            or 0
        )

    amount_paid.short_description = "Amount Paid"

    def remaining_amount(self, obj):
        paid = self.amount_paid(obj)
        return max(obj.total - paid, 0)

    remaining_amount.short_description = "Remaining Amount"

    def is_paid(self, obj):
        return self.remaining_amount(obj) <= 0

    is_paid.boolean = True  # Show a tick/cross icon in admin
    is_paid.short_description = "Paid?"

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
