from django.db import models
from django.conf import settings

from apps.organizations.models import Organization
from apps.master.models import Country

User = settings.AUTH_USER_MODEL


# ----------------------- Purchase Invoice (Purchase Entry) -----------------------
# Defined before other models to avoid forward references; actual class bodies are at end of file.

# -------------------------- VAT Master Model --------------------------
class VATMaster(models.Model):

    vatid = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
    )

    vatname = models.CharField(max_length=191)
    vatnamear = models.CharField(max_length=191, blank=True, null=True)
    vatper = models.DecimalField(max_digits=5, decimal_places=2)

    is_active = models.BooleanField(default=True)

    #mapped from compname / branchname
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_vats_org"
    )

    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="purchase_vats_branches"
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

    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, null=True, blank=True)

    mobile = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)

    address = models.TextField(null=True, blank=True)

    # UPDATED: FK → CharField
    country = models.CharField(max_length=100, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suppliers_org"
    )

    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="suppliers_branches"
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

    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_groups_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="purchase_groups_branches"
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

    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_brands_org",
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="purchase_brands_branches"
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

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="itgrp_organizations",
        help_text="Main organization"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="itgrp_branches"
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

    is_active = models.BooleanField(default=True)

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

    unitname = models.CharField(max_length=191)
    unitnamear = models.CharField(max_length=191, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_units_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="purchase_units_branches"
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

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_items_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="purchase_items_branches"
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

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unitmap_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="unitmap_branches"
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


# ----------------------- VR Type Master Model -----------------------
class VRTypeMaster(models.Model):

    vrname = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vrtype_org",
        help_text="Top-level organization"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="vrtype_branches"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vrtype_created_by"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vrtype_updated_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vrname


# ----------------------- Inventory Transaction Model -----------------------
class INV_TRAN(models.Model):

    # Foreign Keys
    item = models.ForeignKey(
        ItemMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inv_transactions_item",
    )

    unit = models.ForeignKey(
        UnitMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inv_transactions_unit",
    )

    vr_type = models.ForeignKey(
        VRTypeMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inv_transactions_vrtype",
    )

    # Transaction fields
    qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    # Organization / Branch
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_inv_transactions_org",
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="purchase_inv_transactions_branches",
    )

    is_active = models.BooleanField(default=True)

    # Audit fields
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inv_transactions_created",
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inv_transactions_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"INV_TRAN #{self.id}"
    

# ----------------------- Account Transaction Model -----------------------
from django.utils import timezone
from django.db.models import Max
import re

class ACC_TRAN(models.Model):
    PAYMODE_CHOICES = [
        ("NULL", "NULL"),
        ("Cash", "Cash"),
        ("Bank", "Bank"),
    ]

    # Django ID as PK
    id = models.AutoField(primary_key=True)

    # Auto-generated unique voucher number
    vrno = models.CharField(max_length=80, unique=True, editable=False)

    # UPDATED: FK → CharField
    country = models.CharField(max_length=100, blank=True, null=True)

    serial_no = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default=None
    )

    voucher_date = models.DateField(default=timezone.now)

    vr_type = models.ForeignKey(
        VRTypeMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acc_transactions_vrtype"
    )

    # Amounts
    amount_ex_vat = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    vat_amount = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    amount_inc_vat = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    reference_no = models.CharField(max_length=50, blank=True, null=True)
    reference_date = models.DateField(blank=True, null=True)

    paymode = models.CharField(max_length=10, choices=PAYMODE_CHOICES, default="NULL")
    paid_to = models.CharField(max_length=191, blank=True, null=True)
    vatin = models.CharField(max_length=50, blank=True, null=True)

    vat = models.ForeignKey(
        VATMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acc_transactions_vat"
    )

    narration = models.CharField(max_length=200, blank=True, null=True)

    # Organization / Branch
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acc_transactions_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="acc_transactions_branches"
    )

    is_active = models.BooleanField(default=True)

    # Audit fields
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acc_transactions_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acc_transactions_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Transaction"
        verbose_name_plural = "Account Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.vrno} - {self.paid_to or ''} - {self.amount_inc_vat}"

    # ---------------- VRNO AUTO GENERATION ----------------
    def save(self, *args, **kwargs):
        # ---------------- COUNTRY CODE ----------------
        country_code = (self.country if self.country else "01")[:2]

        # ---------------- ENTITY CODE (ORG or BRANCH) ----------------
        user = self.created_by or self.updated_by

        if self.organization:
            entity_code = str(self.organization.id)
        else:
            # Branch-only user → use branch ID
            if user and user.branches.exists():
                entity_code = str(user.branches.first().id)
            else:
                entity_code = "01"   # fallback
        # Ensure minimum 2 digits
        entity_code = entity_code.zfill(2)

        # ---------------- YEAR ----------------
        year = timezone.now().year

        # ---------------- PREFIX FROM VR TYPE ----------------
        type_name = (self.vr_type.vrname.lower() if self.vr_type else "purchase")
        prefix_map = {
            "purchase": "PIV",
            "material consumption": "RMC",
            "damage": "DAM",
        }
        prefix = prefix_map.get(type_name, "PIV")

        # ---------------- VRNO GENERATION ----------------
        if not self.vrno:

            # limit VRNO search **by entity**
            qs = ACC_TRAN.objects.filter(
                vrno__startswith=f"{country_code}{entity_code}{year}{prefix}"
            ).order_by("-vrno")

            last = qs.first()

            if last:
                # extract last number
                match = re.search(r"(\d+)$", last.vrno)
                last_series = int(match.group(1)) if match else 999
                series = last_series + 1
            else:
                series = 1000   # starting series

            self.vrno = f"{country_code}{entity_code}{year}{prefix}{series}"

        # -------- SERIAL NO --------
        if not self.serial_no:
            last_sr = ACC_TRAN.objects.filter(vrno=self.vrno).aggregate(
                Max("serial_no")
            )["serial_no__max"] or 0
            self.serial_no = last_sr + 1

        # -------- VAT CALC --------
        vat_rate = (self.vat.vatper / 100) if self.vat else 0
        self.vat_amount = (self.amount_ex_vat or 0) * vat_rate
        self.amount_inc_vat = (self.amount_ex_vat or 0) + self.vat_amount

        super().save(*args, **kwargs)


# ----------------------- Account Master Model -----------------------
class ACCT_MAST(models.Model):

    BAL_TYPE_CHOICES = [
        ("Debit", "Debit"),
        ("Credit", "Credit"),
    ]

    GRP_CODE_CHOICES = [
        ("ASSET", "ASSET"),
        ("LIABILITY", "LIABILITY"),
        ("INCOME", "INCOME"),
        ("EXPENSE", "EXPENSE"),
    ]

    AC_TYPE_CHOICES = [
        ("General / Group", "General / Group"),
        ("Detail", "Detail"),
    ]

    # Django PK
    id = models.AutoField(primary_key=True)

    # Auto-generated account number (OLD acno)
    acno = models.PositiveIntegerField(editable=False, unique=True)

    accname = models.CharField(max_length=200)
    accname_ar = models.CharField(max_length=200, blank=True, null=True)

    grpcode = models.CharField(
        max_length=20,
        choices=GRP_CODE_CHOICES,
        null=True,
        blank=True,
    )

    baltype = models.CharField(max_length=10, choices=BAL_TYPE_CHOICES)
    actype = models.CharField(max_length=20, choices=AC_TYPE_CHOICES)

    # Auto-generated mapping number
    acmapno = models.PositiveIntegerField(editable=False)

    opening_balance = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    curbal = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    # Organization / Branch
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acct_mast_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="acct_mast_branches"
    )

    is_active = models.BooleanField(default=True)

    # Audit fields
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acct_mast_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acct_mast_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Master"
        verbose_name_plural = "Account Masters"
        ordering = ["acno"]

    def save(self, *args, **kwargs):
        # Auto increment acno
        if not self.acno:
            last = ACCT_MAST.objects.order_by("-acno").first()
            self.acno = (last.acno + 1) if last else 200000

        # Auto increment acmapno
        if not self.acmapno:
            last_map = ACCT_MAST.objects.order_by("-acmapno").first()
            self.acmapno = (last_map.acmapno + 1) if last_map else 10000

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.acno} - {self.accname}"


# ----------------------- Account Master Mapping Model -----------------------
class ACCT_MAST_MAP(models.Model):

    id = models.AutoField(primary_key=True)

    # Auto-generated mapping number
    acmapno = models.PositiveIntegerField(editable=False, unique=True)

    # Total levels
    totlev = models.PositiveIntegerField(default=1)

    # Level mappings
    lev1 = models.PositiveIntegerField(null=True, blank=True)
    lev2 = models.PositiveIntegerField(null=True, blank=True)
    lev3 = models.PositiveIntegerField(null=True, blank=True)
    lev4 = models.PositiveIntegerField(null=True, blank=True)
    lev5 = models.PositiveIntegerField(null=True, blank=True)
    lev6 = models.PositiveIntegerField(null=True, blank=True)
    lev7 = models.PositiveIntegerField(null=True, blank=True)
    lev8 = models.PositiveIntegerField(null=True, blank=True)

    # Organization / Branch
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acctmastmap_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="acctmastmap_branches"
    )

    is_active = models.BooleanField(default=True)

    # Audit fields
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acctmastmap_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acctmastmap_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Master Mapping"
        verbose_name_plural = "Account Master Mappings"
        ordering = ["acmapno"]

    def __str__(self):
        return f"{self.acmapno} - Mapping Levels ({self.totlev})"

    # Auto-generate mapping number like ACCT_MAST
    def save(self, *args, **kwargs):
        if not self.acmapno:
            last = ACCT_MAST_MAP.objects.order_by("-acmapno").first()
            self.acmapno = (last.acmapno + 1) if last else 10000

        super().save(*args, **kwargs)


# ----------------------- Account Transaction Detail Model -----------------------
class ACC_TRAN_DETA(models.Model):

    DCFLAG_CHOICES = [
        ("Debit", "Debit"),
        ("Credit", "Credit"),
    ]

    # Django ID (Primary Key)
    id = models.AutoField(primary_key=True)

    # Relation to ACC_TRAN (Voucher Header)
    acc_tran = models.ForeignKey(
        ACC_TRAN,
        on_delete=models.CASCADE,
        related_name="details"
    )

    voucher_date = models.DateField(default=timezone.localdate)

    vr_type = models.ForeignKey(
        VRTypeMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acc_tran_details_vrtype"
    )

    # Auto-generated serial number inside voucher
    serial_no = models.PositiveIntegerField(editable=False, null=True, blank=True)

    dc_flag = models.CharField(max_length=10, choices=DCFLAG_CHOICES)

    account = models.ForeignKey(
        ACCT_MAST,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acc_tran_details_account"
    )

    list_code_ac = models.CharField(max_length=50, null=True, blank=True)

    amount = models.DecimalField(max_digits=18, decimal_places=3, default=0.000)

    remark = models.CharField(max_length=200, null=True, blank=True)

    # Organization / Branch
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acc_tran_details_org"
    )

    branches = models.ManyToManyField(
        Organization, blank=True,
        related_name="acc_tran_details_branches"
    )

    is_active = models.BooleanField(default=True)

    # Audit fields
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acc_tran_details_created"
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acc_tran_details_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Transaction Detail"
        verbose_name_plural = "Account Transaction Details"
        ordering = ["acc_tran", "serial_no"]

    def __str__(self):
        return f"{self.acc_tran.vrno} - {self.serial_no} - {self.account} - {self.amount}"

    # ----------------- Auto Logic ------------------
    def save(self, *args, **kwargs):

        # Auto-assign serial number within voucher
        if not self.serial_no:
            last = (
                ACC_TRAN_DETA.objects
                .filter(acc_tran=self.acc_tran)
                .order_by("-serial_no")
                .first()
            )
            self.serial_no = (last.serial_no + 1) if last else 1

        # Auto-derive account from list_code_ac
        if not self.account and self.list_code_ac:
            self.account = ACCT_MAST.objects.filter(listcode=self.list_code_ac).first()

        super().save(*args, **kwargs)


# ----------------------- Purchase Invoice Header -----------------------
class PurchaseInvoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    PAYMODE_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("credit", "Credit"),
    ]

    invoice_no = models.CharField(max_length=50, unique=True, editable=False)
    supplier = models.ForeignKey(
        SupplierMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoices"
    )
    vr_type = models.ForeignKey(
        VRTypeMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoices_vrtype"
    )
    vat = models.ForeignKey(
        VATMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoices_vat"
    )
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    paymode = models.CharField(max_length=10, choices=PAYMODE_CHOICES, default="cash")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    amount_ex_vat = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    vat_amount = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    amount_inc_vat = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    narration = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoices_org"
    )
    branches = models.ManyToManyField(
        Organization, blank=True, related_name="purchase_invoices_branches"
    )
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoices_created"
    )
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoices_updated"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Purchase Invoice"
        verbose_name_plural = "Purchase Invoices"
        ordering = ["-invoice_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            last = PurchaseInvoice.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.invoice_no = f"PIV{next_id:05d}"
        # Recalculate VAT
        vat_rate = (self.vat.vatper / 100) if self.vat else 0
        self.vat_amount = (self.amount_ex_vat or 0) * vat_rate
        self.amount_inc_vat = (self.amount_ex_vat or 0) + self.vat_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_no} - {self.supplier}"


# ----------------------- Purchase Invoice Line -----------------------
class PurchaseInvoiceLine(models.Model):
    invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE,
        related_name="lines"
    )
    item = models.ForeignKey(
        ItemMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="invoice_lines"
    )
    unit = models.ForeignKey(
        UnitMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="invoice_lines_unit"
    )
    qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoice_lines_org"
    )
    branches = models.ManyToManyField(
        Organization, blank=True, related_name="purchase_invoice_lines_branches"
    )
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoice_lines_created"
    )
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_invoice_lines_updated"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Purchase Invoice Line"
        verbose_name_plural = "Purchase Invoice Lines"
        ordering = ["invoice", "id"]

    def save(self, *args, **kwargs):
        # Auto-calculate amount if not provided
        if self.qty and self.rate:
            self.amount = self.qty * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.item} x {self.qty}"