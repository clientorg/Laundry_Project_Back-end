from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.functions import Coalesce
from django.db.models import Sum, Q, F, DecimalField, ExpressionWrapper

# laundry model imports
from apps.customers.models import Customer
from apps.organizations.models import Organization

# Create your models here.
User = get_user_model()


class OrderQuerySet(models.QuerySet):
    def with_unpaid_credit(self, tolerance=Decimal("0.99")):
        """
        Annotate orders with total credit & repayment,
        and filter only those with unpaid balance.
        """
        return (
            self.filter(payments__payment_type="credit")
            .distinct()
            .annotate(
                total_credit=Coalesce(
                    Sum(
                        "payments__received_amount",
                        filter=Q(payments__payment_type="credit"),
                    ),
                    Decimal("0.000"),
                ),
                total_repaid=Coalesce(
                    Sum(
                        "payments__received_amount",
                        filter=Q(payments__payment_type="repayment"),
                    ),
                    Decimal("0.000"),
                ),
            )
            .filter(
                total_credit__gt=ExpressionWrapper(
                    F("total_repaid") + tolerance,
                    output_field=DecimalField(max_digits=12, decimal_places=3),
                ),
            )
        )


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def with_unpaid_credit(self, tolerance=0.99):
        return self.get_queryset().with_unpaid_credit(tolerance=tolerance)


class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    is_carpet = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
    data = models.JSONField(default=dict)

    delivery_charge_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    delivery_charge_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
    )

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
    )

    vat_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
    )
    vat_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        blank=True,
        default=0.000,
    )

    inward_date = models.DateField(
        blank=True,
        null=True,
        auto_now_add=True,
        help_text="Date when the order was received.",
    )
    delivery_date = models.DateField(
        blank=True,
        null=True,
        help_text="Planned delivery date.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        help_text="The customer who placed this order.",
    )

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        help_text="The main organization this order belongs to. Optional if shared across branches.",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="order_branches",
        help_text="Branches where this order is available.",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="orders_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="orders_updated",
        on_delete=models.SET_NULL,
    )

    objects = OrderManager()

    def save(self, *args, **kwargs):
        if not self.order_id:
            last_order = Order.objects.order_by("-id").first()
            next_id = 1 if not last_order else last_order.id + 1
            self.order_id = f"ORD{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    remarks = models.TextField(blank=True, null=True)

    cloth_name = models.CharField(max_length=100)
    cloth_arabic_name = models.CharField(max_length=100, blank=True, null=True)
    cloth_price = price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
    )

    service_name = models.CharField(max_length=100, blank=True, null=True)
    service_price = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    handling_name = models.CharField(max_length=100, blank=True, null=True)
    handling_price = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    delivery_name = models.CharField(max_length=100)
    delivery_charge_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    customer_category_name = models.CharField(max_length=50)
    customer_category_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    customer_category_discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
    )

    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        default=0.00,
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        default=0.00,
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        default=0.000,
    )
    rate_per_area = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        default=0.000,
    )
    area_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        default=0.000,
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        blank=True,
        default=0.000,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="order_items_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="order_items_updated",
        on_delete=models.SET_NULL,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cloth_name} x {self.quantity} (Order #{self.order.order_id})"


class OrderPayment(models.Model):
    PAYMENT_TYPES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("upi", "UPI"),
        ("wallet", "Wallet"),
        ("repayment", "Repayment"),
        ("credit", "Credit"),
        ("other", "Other"),
    ]

    note = models.TextField(blank=True, null=True)
    apply_rounding = models.BooleanField(default=False)
    rating = models.CharField(max_length=10, blank=True, null=True)
    rating_link = models.BooleanField(
        default=False,
    )
    rounding_amount = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.000
    )
    received_amount = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0.000,
        help_text="Amount received in this payment",
    )
    change_return = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
        help_text="Change returned to the customer",
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        help_text="Payment method (cash, card, credit, etc.)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order = models.ForeignKey(
        Order,
        related_name="payments",
        on_delete=models.CASCADE,
        help_text="The order this payment belongs to.",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="payment_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="payment_updated",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.payment_type.title()} payment of {self.received_amount} for Order #{self.order.order_id}"
