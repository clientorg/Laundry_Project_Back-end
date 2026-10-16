from django.contrib import admin

from .models import VATMaster
from apps.organizations.models import Organization


@admin.register(VATMaster)
class VATMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "vatname",
        "vatper",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    search_fields = (
        "vatname",
        "vatnamear",
        "vatper",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "vatid",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "VAT Information",
            {
                "fields": (
                    "vatname",
                    "vatnamear",
                    "vatper",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
            {
                "fields": (
                    "vatid",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    # ---------------- CUSTOM METHODS ----------------
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORG & BRANCHES ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------SUPPLIER MASTER ADMIN --------------------
from .models import SupplierMaster

@admin.register(SupplierMaster)
class SupplierMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "name",
        "mobile_no",
        "email",
        "country",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    search_fields = (
        "name",
        "name_ar",
        "mobile",
        "email",
        "country",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Supplier Information",
            {
                "fields": (
                    "name",
                    "name_ar",
                    "mobile",
                    "email",
                    "country",
                    "address",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM METHODS ----------------
    def mobile_no(self, obj):
        return obj.mobile or "—"
    mobile_no.short_description = "Mobile"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------GROUP MASTER ADMIN --------------------
from .models import GroupMaster

@admin.register(GroupMaster)
class GroupMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "name",
        "name_ar",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    search_fields = (
        "name",
        "name_ar",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Group Information",
            {
                "fields": (
                    "name",
                    "name_ar",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM METHODS ----------------
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------BRAND MASTER ADMIN --------------------
from .models import BrandMaster

@admin.register(BrandMaster)
class BrandMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "name",
        "name_ar",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    search_fields = (
        "name",
        "name_ar",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Brand Information",
            {
                "fields": (
                    "name",
                    "name_ar",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM METHODS ----------------
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------ITGRP_MAP ADMIN --------------------
from .models import ITGRP_MAP

@admin.register(ITGRP_MAP)
class ITGRP_MAPAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "id",
        "grp_name",
        "brand_name",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    search_fields = (
        "grpcode__name",
        "brdcode__name",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Group–Brand Mapping",
            {
                "fields": (
                    "grpcode",
                    "brdcode",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM METHODS ----------------
    def grp_name(self, obj):
        return obj.grpcode.name if obj.grpcode else "—"
    grp_name.short_description = "Group Name"

    def brand_name(self, obj):
        return obj.brdcode.name if obj.brdcode else "—"
    brand_name.short_description = "Brand Name"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------UNIT MASTER ADMIN --------------------
from .models import UnitMaster

@admin.register(UnitMaster)
class UnitMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "unitname",
        "unitnamear",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    search_fields = (
        "unitname",
        "unitnamear",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Unit Information",
            {
                "fields": (
                    "unitname",
                    "unitnamear",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM METHODS ----------------
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------ITEM MASTER ADMIN --------------------
from .models import ItemMaster

@admin.register(ItemMaster)
class ItemMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "itname",
        "unit_name",
        "group_name",
        "brand_name",
        "supplier_name",
        "vat_name",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization", "unit", "group_map", "supplier", "vat")

    search_fields = (
        "itname",
        "itnamear",
        "unit__unitname",
        "group_map__grpcode__name",
        "group_map__brdcode__name",
        "supplier__name",
        "vat__vatname",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Item Information",
            {
                "fields": (
                    "itname",
                    "itnamear",
                    "dubcost",
                    "impcost",
                    "itcost",
                    "rtrate",
                    "vatrate",
                    "is_active",
                )
            },
        ),
        (
            "Relationships",
            {
                "fields": (
                    "unit",
                    "group_map",
                    "supplier",
                    "vat",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM DISPLAY METHODS ----------------
    def unit_name(self, obj):
        return obj.unit.unitname if obj.unit else "—"
    unit_name.short_description = "Unit Name"

    def group_name(self, obj):
        if obj.group_map and obj.group_map.grpcode:
            return obj.group_map.grpcode.name
        return "—"
    group_name.short_description = "Group Name"

    def brand_name(self, obj):
        if obj.group_map and obj.group_map.brdcode:
            return obj.group_map.brdcode.name
        return "—"
    brand_name.short_description = "Brand Name"

    def supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else "—"
    supplier_name.short_description = "Supplier Name"

    def vat_name(self, obj):
        return obj.vat.vatname if obj.vat else "—"
    vat_name.short_description = "VAT Name"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------UNIT MAP ADMIN --------------------
from .models import UnitMap

@admin.register(UnitMap)
class UnitMapAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "item_name",
        "unit_name",
        "qty",
        "alt_unit_name",
        "alt_qty",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization", "unit", "alt_unit")
    
    search_fields = (
        "item__itname",
        "unit__unitname",
        "alt_unit__unitname",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Unit Mapping Details",
            {
                "fields": (
                    "item",
                    "unit",
                    "qty",
                    "alt_unit",
                    "alt_qty",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM DISPLAY METHODS ----------------
    def item_name(self, obj):
        return obj.item.itname if obj.item else "—"
    item_name.short_description = "Item Name"

    def unit_name(self, obj):
        return obj.unit.unitname if obj.unit else "—"
    unit_name.short_description = "Unit Name"

    def alt_unit_name(self, obj):
        return obj.alt_unit.unitname if obj.alt_unit else "—"
    alt_unit_name.short_description = "Alternate Unit Name"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCH ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------VR TYPE MASTER ADMIN --------------------
from .models import VRTypeMaster

@admin.register(VRTypeMaster)
class VRTypeMasterAdmin(admin.ModelAdmin):

    # ---------------- TABLE DISPLAY ----------------
    list_display = (
        "vrname",
        "zipcode",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization")
    
    search_fields = (
        "vrname",
        "zipcode",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ---------------- READONLY FIELDS ----------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ---------------- FORM LAYOUT ----------------
    fieldsets = (
        (
            "Voucher Type Information",
            {
                "fields": (
                    "vrname",
                    "zipcode",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ---------------- CUSTOM METHODS ----------------
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------------- FILTER ORGANIZATION & BRANCHES ----------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------------- AUTO SET CREATED/UPDATED BY ----------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------INV TRAN ADMIN --------------------
from .models import INV_TRAN

@admin.register(INV_TRAN)
class INVTRANAdmin(admin.ModelAdmin):

    # ------------- TABLE DISPLAY -------------
    list_display = (
        "item_name",
        "unit_name",
        "qty",
        "rate",
        "amount",
        "vr_type_name",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("is_active", "organization", "vr_type", "unit")

    search_fields = (
        "item__itname",
        "unit__unitname",
        "vr_type__vrname",
        "organization__name",
        "branches__name",
        "created_by__username",
        "updated_by__username",
    )

    filter_horizontal = ("branches",)

    # ------------- READONLY FIELDS -------------
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    # ------------- FORM LAYOUT -------------
    fieldsets = (
        (
            "Inventory Transaction",
            {
                "fields": (
                    "item",
                    "unit",
                    "vr_type",
                    "qty",
                    "rate",
                    "amount",
                    "is_active",
                )
            },
        ),
        (
            "Organization & Branches",
            {
                "fields": (
                    "organization",
                    "branches",
                )
            },
        ),
        (
            "Meta Information",
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

    # ------------- CUSTOM DISPLAY METHODS -------------
    def item_name(self, obj):
        return obj.item.itname if obj.item else "—"
    item_name.short_description = "Item Name"

    def unit_name(self, obj):
        return obj.unit.unitname if obj.unit else "—"
    unit_name.short_description = "Unit Name"

    def vr_type_name(self, obj):
        return obj.vr_type.vrname if obj.vr_type else "—"
    vr_type_name.short_description = "Voucher Type Name"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ------------- ORG / BRANCH FILTERING -------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ------------- AUTO SET CREATED/UPDATED BY -------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


from .models import ACC_TRAN
from django import forms

class ACC_TRANForm(forms.ModelForm):
    class Meta:
        model = ACC_TRAN
        fields = "__all__"
        labels = {
            "amount_ex_vat": "Net Amount (Excluding VAT)",
            "amount_inc_vat": "Total Amount (Including VAT)",
            "vrno": "Voucher Number",
            "vr_type": "Voucher Type",
            "country": "Country (Dial Code)",
        }

@admin.register(ACC_TRAN)
class ACCTRANAdmin(admin.ModelAdmin):
    form = ACC_TRANForm
    # -------- TABLE DISPLAY --------
    list_display = (
        "vrno",
        "voucher_date",
        "vr_type_name",
        "amount_ex_vat_display",
        "vat_amount",
        "amount_inc_vat_display",
        "paymode",
        "paid_to",
        "organization",
        "branches_count",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = ("organization", "vr_type", "paymode", "voucher_date")
    
    search_fields = (
        "vrno",
        "paid_to",
        "reference_no",
        "narration",
        "vr_type__vrname",
        "vat__vatname",
        "organization__name",
        "branches__name",
    )

    filter_horizontal = ("branches",)

    # -------- READONLY FIELDS --------
    readonly_fields = (
        "vrno",
        "serial_no",
        "vat_amount",
        "amount_inc_vat",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    # -------- FORM LAYOUT --------
    fieldsets = (
        ("Voucher Information", {
            "fields": (
                "vrno",
                "serial_no",
                "voucher_date",
                "vr_type",
                "narration",
            )
        }),

        ("Amounts", {
            "fields": (
                "amount_ex_vat",
                "vat",
                "vat_amount",
                "amount_inc_vat",
            )
        }),

        ("References", {
            "fields": (
                "reference_no",
                "reference_date",
            )
        }),

        ("Payment Info", {
            "fields": (
                "paymode",
                "paid_to",
                "vatin",
            )
        }),

        ("Organization & Branches", {
            "fields": (
                "organization",
                "branches",
                "country",
                "is_active",
            )
        }),

        ("Meta Information", {
            "fields": (
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    # -------- CUSTOM DISPLAY METHODS --------
    def amount_ex_vat_display(self, obj):
        return obj.amount_ex_vat
    amount_ex_vat_display.short_description = "Net Amount (Exc VAT)"

    def amount_inc_vat_display(self, obj):
        return obj.amount_inc_vat
    amount_inc_vat_display.short_description = "Total Amount (Inc VAT)"
    
    def vr_type_name(self, obj):
        return obj.vr_type.vrname if obj.vr_type else "—"
    vr_type_name.short_description = "Voucher Type Name"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # -------- ORG / BRANCH FILTERING --------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # -------- AUTO SET CREATED/UPDATED BY --------
    def save_model(self, request, obj, form, change):
        if not obj.pk:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


from .models import ACCT_MAST

class ACCT_MASTForm(forms.ModelForm):
    class Meta:
        model = ACCT_MAST
        fields = "__all__"
        labels = {
            "acno": "Account No",
            "accname": "Account Name",
            "accname_ar": "Account Name (Arabic)",
            "grpcode": "Group Code",
            "baltype": "Balance Type",
            "actype": "Account Type",
            "curbal": "Current Balance",
            "acmapno": "Account Map No",
            "parent": "Parent Account (must be a Group account)",
        }

@admin.register(ACCT_MAST)
class ACCTMASTAdmin(admin.ModelAdmin):
    form = ACCT_MASTForm 
    # ---------- TABLE VIEW ----------
    list_display = (
        "acno",
        "account_name",
        "balance_type",
        "account_type",
        "parent",
        "opening_balance",
        "current_balance",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = (
        "grpcode",
        "baltype",
        "actype",
        "organization",
        "is_active",
    )

    search_fields = (
        "acno",
        "accname",
        "accname_ar",
        "organization__name",
        "branches__name",
    )

    filter_horizontal = ("branches",)

    # ---------- READONLY FIELDS ----------
    readonly_fields = (
        "acno",
        "acmapno",      # readonly → leave default header, do NOT rename
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    # ---------- FORM LAYOUT ----------
    fieldsets = (
        ("Account Info", {
            "fields": (
                "acno",
                "accname",
                "accname_ar",
                "grpcode",
                "baltype",
                "actype",
                "parent",
            )
        }),

        ("Balances", {
            "fields": (
                "opening_balance",
                "curbal",
            )
        }),

        ("Organization & Branches", {
            "fields": (
                "organization",
                "branches",
                "is_active",
            )
        }),

        ("Meta Data", {
            "fields": (
                "acmapno",
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    # ---------- CUSTOM DISPLAY METHODS (Renamed Columns) ----------
    def account_name(self, obj):
        return obj.accname
    account_name.short_description = "Account Name"

    def balance_type(self, obj):
        return obj.baltype
    balance_type.short_description = "Balance Type"

    def account_type(self, obj):
        return obj.actype
    account_type.short_description = "Account Type"

    def current_balance(self, obj):
        return obj.curbal
    current_balance.short_description = "Current Balance"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------- ORG / BRANCH FILTERING ----------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        elif db_field.name == "parent":
            kwargs["queryset"] = ACCT_MAST.objects.filter(actype=ACCT_MAST.GROUP)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------- AUTO SET CREATED / UPDATED BY ----------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --------------------ACCT MAST MAP ADMIN --------------------
from .models import ACCT_MAST_MAP

@admin.register(ACCT_MAST_MAP)
class ACCTMASTMAPAdmin(admin.ModelAdmin):
    """
    Read-only: rows are auto-derived from ACCT_MAST.parent (see ACCT_MAST._cascade_level_map).
    To change the hierarchy, edit `parent` on the Account Master record instead.
    """

    # ---------- TABLE VIEW ----------
    list_display = (
        "acmapno",
        "acct_mast",
        "totlev",
        "organization",
        "branches_count",
        "is_active",
        "created_at",
    )

    list_filter = (
        "totlev",
        "organization",
        "is_active",
    )

    search_fields = (
        "acmapno",
        "acct_mast__accname",
        "organization__name",
        "branches__name",
    )

    # ---------- FORM LAYOUT ----------
    fieldsets = (
        ("Mapping Info", {
            "fields": (
                "acct_mast",
                "acmapno",
                "totlev",
                "lev1",
                "lev2",
                "lev3",
                "lev4",
                "lev5",
                "lev6",
                "lev7",
                "lev8",
            )
        }),

        ("Organization & Branches", {
            "fields": (
                "organization",
                "branches",
                "is_active",
            )
        }),

        ("Meta Information", {
            "fields": (
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    # ---------- CUSTOM DISPLAY METHODS ----------
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


# --------------------ACC TRAN DETA ADMIN --------------------
from .models import ACC_TRAN_DETA
class ACC_TRAN_DETAForm(forms.ModelForm):
    class Meta:
        model = ACC_TRAN_DETA
        fields = "__all__"
        labels = {
            "acc_tran": "Account Transaction",
            "dc_flag": "Debit/Credit Flag",
            "list_code_ac": "Account List Code",
            "vr_type": "Voucher Type",
        }

@admin.register(ACC_TRAN_DETA)
class ACCTRANDETAAdmin(admin.ModelAdmin):
    form = ACC_TRAN_DETAForm
    # ---------- TABLE VIEW ----------
    list_display = (
        "acc_tran_vrno",
        "serial_no",
        "voucher_date",
        "vr_type_name",
        "dc_flag",
        "account_name",
        "amount",
        "organization",
        "branches_count",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = (
        "dc_flag",
        "vr_type",
        "organization",
        "is_active",
    )

    search_fields = (
        "acc_tran__vrno",
        "account__accname",
        "remark",
        "organization__name",
        "branches__name",
    )

    filter_horizontal = ("branches",)

    # ---------- READONLY FIELDS ----------
    readonly_fields = (
        "serial_no",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    # ---------- FORM LAYOUT ----------
    fieldsets = (
        ("Transaction Detail", {
            "fields": (
                "acc_tran",
                "serial_no",
                "voucher_date",
                "vr_type",
                "dc_flag",
                "account",
                "list_code_ac",
                "amount",
                "remark",
                "is_active",
            )
        }),

        ("Organization & Branches", {
            "fields": (
                "organization",
                "branches",
            )
        }),

        ("Audit Info", {
            "fields": (
                "created_by",
                "updated_by",
                "created_at",
                "updated_at"
            ),
            "classes": ("collapse",),
        }),
    )

    # ---------- CUSTOM DISPLAY METHODS ----------
    def acc_tran_vrno(self, obj):
        return obj.acc_tran.vrno if obj.acc_tran else "—"
    acc_tran_vrno.short_description = "Voucher No"

    def vr_type_name(self, obj):
        return obj.vr_type.vrname if obj.vr_type else "—"
    vr_type_name.short_description = "Voucher Type"

    def account_name(self, obj):
        return obj.account.accname if obj.account else "—"
    account_name.short_description = "Account Name"

    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = "Branches"

    # ---------- ORG / BRANCH FILTERING ----------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ---------- AUTO SET CREATED / UPDATED BY ----------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)