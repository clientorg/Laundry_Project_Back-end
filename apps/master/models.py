from django.db import models
from django.contrib.auth import get_user_model

# laundry model imports
from apps.organizations.models import Organization


# Create your models here.
User = get_user_model()


class ClothType(models.Model):
    # table fields
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    # table non-editable fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # relations
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_cloth_types",
        help_text="The main organization this cloth type belongs to. Optional if shared across branches.",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_cloth_types",
        help_text="Branches where this cloth type is available.",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="cloth_types_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="cloth_types_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Cloth Type"
        verbose_name_plural = "Cloth Types"

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_washing_types",
        help_text="The main/root organization of the service type",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_washing_types",
        help_text="Branches where this service type is available",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="service_types_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="service_types_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Service Type"
        verbose_name_plural = "Service Types"

    def __str__(self):
        return self.name


class HandlingType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_handling_types",
        help_text="The main/root organization of the handling type",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_handling_types",
        help_text="Branches where this handling type is available",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="handling_types_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="handling_types_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Handling Type"
        verbose_name_plural = "Handling Types"

    def __str__(self):
        return self.name


class DeliveryType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_delivery_types",
        help_text="The main/root organization of the delivery type",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_delivery_types",
        help_text="Branches where this delivery type is available",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="delivery_types_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="delivery_types_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Delivery Type"
        verbose_name_plural = "Delivery Types"

    def __str__(self):
        return self.name
