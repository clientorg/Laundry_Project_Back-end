from django.db import models
from django.conf import settings
from apps.organizations.models import Organization
from apps.purchase.models import VRTypeMaster, VATMaster

User = settings.AUTH_USER_MODEL


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=191)
    name_ar = models.CharField(max_length=191, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expense_categories_org"
    )
    branches = models.ManyToManyField(
        Organization, blank=True, related_name="expense_categories_branches"
    )
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expense_categories_created"
    )
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expense_categories_updated"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    expense_no = models.CharField(max_length=50, unique=True, editable=False)
    category = models.ForeignKey(
        ExpenseCategory, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expenses"
    )
    vr_type = models.ForeignKey(
        VRTypeMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expenses_vrtype"
    )
    vat = models.ForeignKey(
        VATMaster, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expenses_vat"
    )
    amount = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    amount_ex_vat = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    vat_amount = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    total_incl_vat = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    paid_to = models.CharField(max_length=191, blank=True, null=True)
    narration = models.CharField(max_length=200, blank=True, null=True)
    expense_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    payment_mode = models.CharField(max_length=50, blank=True, null=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expenses_org"
    )
    branches = models.ManyToManyField(
        Organization, blank=True, related_name="expenses_branches"
    )
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expenses_created"
    )
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="expenses_updated"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ["-expense_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.expense_no:
            last = Expense.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.expense_no = f"EXP{next_id:05d}"
        vat_rate = (self.vat.vatper / 100) if self.vat else 0
        self.vat_amount = (self.amount_ex_vat or 0) * vat_rate
        self.total_incl_vat = (self.amount_ex_vat or 0) + self.vat_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.expense_no} - {self.amount}"
