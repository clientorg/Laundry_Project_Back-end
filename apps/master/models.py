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


class WashingType(models.Model):
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
        help_text="The main/root organization of the washing type",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_washing_types",
        help_text="Branches where this washing type is available",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="washing_types_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="washing_types_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Washing Type"
        verbose_name_plural = "Washing Types"

    def __str__(self):
        return self.name
