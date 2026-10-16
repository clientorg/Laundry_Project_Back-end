from django.db import models
from django.apps import apps
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

# Laundry Models
from apps.master.models import Country
from apps.organizations.models import Organization

# Create your models here.
User = get_user_model()


class CustomerCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Discount percentage applied to customers in this category (e.g., 10.00 for 10%)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="customer_categories",
        help_text="The main organization this customer category belongs to. Optional if shared across branches.",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_customer_categories",
        help_text="Branches where this customer category is available.",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="customer_categories_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="customer_categories_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Customer Category"
        verbose_name_plural = "Customer Categories"

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"


class Customer(models.Model):
    is_active = models.BooleanField(default=True)
    address = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    mobile_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
    )
    customer_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )
    opening_due = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0.000,
        null=True,
        blank=True,
        help_text="Opening outstanding amount for this customer.",
    )
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0.000,
        null=True,
        blank=True,
        help_text="Maximum credit allowed for this customer.",
    )
    tax_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Tax Identification Number (TIN/VAT/etc.) for this customer.",
    )
    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Customer's email address.",
        validators=[EmailValidator()],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(
        CustomerCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="customers",
        help_text="The category of the customer, e.g., Family, Friends, Employee",
    )
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_customers",
        help_text="The main organization this customer belongs to. Optional if shared across branches.",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_customers",
        help_text="Branches where this customer is available.",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="customers_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="customers_updated",
        on_delete=models.SET_NULL,
    )

    def credit_used(self):
        OrderPayment = apps.get_model("orders", "OrderPayment")
        credit = (
            OrderPayment.objects.filter(
                order__customer=self, payment_type="credit"
            ).aggregate(total=Sum("received_amount"))["total"]
            or 0
        )
        repayment = (
            OrderPayment.objects.filter(
                order__customer=self, payment_type="repayment"
            ).aggregate(total=Sum("received_amount"))["total"]
            or 0
        )
        opening_due = self.opening_due or 0
        return max(0, opening_due + credit - repayment)

    def credit_remaining(self):
        credit_limit = self.credit_limit or 0
        return credit_limit - self.credit_used()

    def balance(self):
        OrderPayment = apps.get_model("orders", "OrderPayment")
        Order = apps.get_model("orders", "Order")

        # Sum of all payments except 'credit'
        total_paid = (
            OrderPayment.objects.filter(order__customer=self)
            .exclude(payment_type="credit")
            .aggregate(total=Sum("received_amount"))["total"]
            or 0
        )

        # Sum of all order totals
        total_orders = (
            Order.objects.filter(customer=self).aggregate(total=Sum("total"))["total"]
            or 0
        )

        return max(0, total_paid - total_orders)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last_customer = Customer.objects.order_by("-id").first()
            next_id = 1 if not last_customer else last_customer.id + 1
            self.customer_id = f"LCS{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Customer #{self.id} by {self.created_by}"
