from django.db import models
from django.contrib.auth import get_user_model

# laundry model imports
from apps.organizations.models import Organization


# Create your models here.
User = get_user_model()


class Country(models.Model):
    name = models.CharField(max_length=100)
    dial_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_main_currency = models.BooleanField(default=False)
    iso_code = models.CharField(max_length=3, unique=True)
    mobile_number_max_digits = models.PositiveIntegerField(default=10)
    flag_emoji = models.CharField(
        max_length=5,
        blank=True,
        null=True,
    )
    luxury_tax_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
    )
    currency_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    currency_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )
    currency_symbol = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )
    service_vat_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0,
    )
    language_name = models.JSONField(
        default=list,
        blank=True,
        null=True,
    )
    language_code = models.JSONField(
        default=list,
        blank=True,
        null=True,
    )
    company_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ["name"]

    def __str__(self):
        return f"{self.flag_emoji} {self.name} ({self.dial_code})"


class Item(models.Model):
    # table fields
    name = models.CharField(max_length=100)
    secondary_name = models.CharField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_size_based_price = models.BooleanField(default=False)

    is_laundry = models.BooleanField(default=False)
    laundry_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )
    is_pressing = models.BooleanField(default=False)
    pressing_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )
    is_dry_clean = models.BooleanField(default=False)
    dry_clean_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )
    is_steam = models.BooleanField(default=False)
    steam_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )

    image = models.ImageField(
        upload_to="item_images/",
        null=True,
        blank=True,
        help_text="Upload an image of the item",
    )

    # table non-editable fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # relations
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_items",
        help_text="The main organization this item belongs to. Optional if shared across branches.",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_items",
        help_text="Branches where this item is available.",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="item_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="item_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self):
        return self.name


class ClothType(models.Model):
    # table fields
    name = models.CharField(max_length=100)
    arabic_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_carpet = models.BooleanField(default=False)
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
    charge_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

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
