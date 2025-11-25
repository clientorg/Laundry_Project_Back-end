from django.db import models
from django.conf import settings

from apps.organizations.models import Organization
from apps.master.models import Country

User = settings.AUTH_USER_MODEL

# -------------------------- VAT Master Model --------------------------
class VATMaster(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    vatid = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
    )

    vatname = models.CharField(max_length=191)
    vatnamear = models.CharField(max_length=191, blank=True, null=True)
    vatper = models.DecimalField(max_digits=5, decimal_places=2)

    accestat = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="0 = inactive, 1 = active"
    )

    #mapped from compname / branchname
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_vats_org"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_vats_branch"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_vats_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_vats_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.vatid:
            last = VATMaster.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.vatid = next_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vatname} ({self.vatper}%)"


# ----------------------- Supplier Master Model -----------------------
class SupplierMaster(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, null=True, blank=True)

    mobile = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)

    address = models.TextField(null=True, blank=True)

    country = models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_suppliers"
    )

    accestat = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1
    )

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suppliers_org"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suppliers_branch"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suppliers_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suppliers_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# ----------------------- Group Master Model -----------------------
class GroupMaster(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, null=True, blank=True)

    accestat = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1
    )

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_groups_org"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_groups_branch"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="groups_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="groups_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
# ----------------------- Brand Master Model -----------------------
class BrandMaster(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, null=True, blank=True)

    accestat = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
    )

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_brands_org",
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_brands_branch",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="brands_created",
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="brands_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ----------------------- ITGRP_MAP Model -----------------------
class ITGRP_MAP(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_organizations",
        help_text="Main organization"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_branches",
        help_text="Branch / Division"
    )

    grpcode = models.ForeignKey(
        GroupMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_groups",
        verbose_name="Group"
    )

    brdcode = models.ForeignKey(
        BrandMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_brands",
        verbose_name="Brand"
    )

    accestat = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="0 = inactive, 1 = active"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ITGRP_MAP #{self.id}"


# ----------------------- Unit Master Model -----------------------
class UnitMaster(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    unitname = models.CharField(max_length=191)
    unitnamear = models.CharField(max_length=191, blank=True, null=True)

    accestat = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="0 = inactive, 1 = active"
    )

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_units_org"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_units_branch"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unit_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unit_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.unitname


# ----------------------- Item Master Model -----------------------
class ItemMaster(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    itname = models.CharField(max_length=191)
    itnamear = models.CharField(max_length=191, blank=True, null=True)

    dubcost = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    impcost = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    itcost = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    rtrate = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    vatrate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    unit = models.ForeignKey(
        UnitMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="items_unit"
    )

    group_map = models.ForeignKey(
        ITGRP_MAP,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="items_groupmap"
    )

    supplier = models.ForeignKey(
        SupplierMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="items_supplier"
    )

    vat = models.ForeignKey(
        VATMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="items_vat"
    )

    accestat = models.IntegerField(choices=STATUS_CHOICES, default=1)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_items_org"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_items_branch"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="item_created_by"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="item_updated_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.itname
    

# ----------------------- Unit Map Model -----------------------
class UnitMap(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    # default Django id will be used

    item = models.ForeignKey(
        ItemMaster,
        on_delete=models.CASCADE,
        related_name="unit_mappings"
    )

    unit = models.ForeignKey(
        UnitMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_unit"
    )

    # optional alternative unit
    alt_unit = models.ForeignKey(
        UnitMaster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_altunit"
    )

    qty = models.DecimalField(max_digits=10, decimal_places=3, default=1)

    # optional alternative quantity
    alt_qty = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        default=None
    )

    accestat = models.IntegerField(choices=STATUS_CHOICES, default=1)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_org"
    )

    branch = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_branch"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UnitMap for {self.item.itname}"
