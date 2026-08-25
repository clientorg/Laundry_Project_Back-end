from django.db import models
from datetime import timedelta
from django.utils import timezone


# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_mobile_number = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    currency_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )
    service_vat_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
    )
    vat_registration_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        "accounts.AuthUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations_created",
    )
    updated_by = models.ForeignKey(
        "accounts.AuthUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations_updated",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="branches",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name


class Branch(Organization):
    class Meta:
        proxy = True
        verbose_name = "Branch"
        verbose_name_plural = "Branches"


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3)

    max_users = models.PositiveIntegerField(default=1)
    max_branches = models.PositiveIntegerField(default=1)

    duration_days = models.PositiveIntegerField(default=30)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationSubscription(models.Model):
    started_at = models.DateTimeField(editable=False)
    expires_at = models.DateTimeField(editable=False)

    organization = models.ForeignKey(
        Organization,
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        Plan,
        related_name="subscriptions",
        on_delete=models.PROTECT,
    )

    @property
    def is_active(self):
        now = timezone.now()
        return self.started_at <= now <= self.expires_at

    def save(self, *args, **kwargs):
        if not self.pk:
            self.started_at = timezone.now()
            self.expires_at = self.started_at + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.organization} -> {self.plan.name} ({'Active' if self.is_active else 'Expired'})"
