from django.db.models import Sum

# package imports
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# laundry model imports
from .models import Order, OrderItem, OrderPayment

# laundry serializer imports
from apps.customers.serializers import CustomerSerializer

# laundry mixin imports
from apps.organizations.mixins import OrgBranchAssignMixin


class OrderItemSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None


class OrderItemInlineSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = (
            "order",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None


class OrderPaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderPayment
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_order_id(self, obj):
        return obj.order.order_id if obj.order else None

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None


class OrderPaymentInlineSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    order_id = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderPayment
        fields = "__all__"
        read_only_fields = (
            "order",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_order_id(self, obj):
        return obj.order.order_id if obj.order else None

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None


class OrderSerializer(serializers.ModelSerializer, OrgBranchAssignMixin):
    customer_name = serializers.SerializerMethodField()
    customer_mobile_number = serializers.SerializerMethodField()
    customer_country_code = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    amount_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    branch_names = serializers.SerializerMethodField()

    items = OrderItemInlineSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.CharField())
    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None

    @extend_schema_field(serializers.CharField())
    def get_customer_mobile_number(self, obj):
        return obj.customer.mobile_number if obj.customer else None

    @extend_schema_field(serializers.CharField())
    def get_customer_country_code(self, obj):
        return obj.customer.country_code if obj.customer else None

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_amount_paid(self, obj):
        return obj.payments.aggregate(total=Sum("received_amount"))["total"] or 0

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_remaining_amount(self, obj):
        return max(obj.total - self.get_amount_paid(obj), 0)

    @extend_schema_field(serializers.BooleanField())
    def get_is_paid(self, obj):
        amount_paid = (
            obj.payments.exclude(payment_type="credit").aggregate(
                total=Sum("received_amount")
            )["total"]
            or 0
        )
        remaining = max(obj.total - amount_paid, 0)
        tolerance = 0.50
        return remaining <= tolerance

    @extend_schema_field(serializers.CharField())
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    @extend_schema_field(serializers.CharField())
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    @extend_schema_field(serializers.CharField())
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    @extend_schema_field(
        serializers.ListSerializer(child=serializers.CharField()),
    )
    def get_branch_names(self, obj):
        return [branch.name for branch in obj.branches.all()]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        validated_data.pop("created_by", None)
        validated_data.pop("updated_by", None)
        user = self.context["request"].user
        validated_data = self.assign_org_branch_on_create(validated_data)
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        branches = validated_data.pop("branches", [])
        order = Order.objects.create(**validated_data)
        if branches:
            order.branches.set(branches)
        for item_data in items_data:
            OrderItem.objects.create(
                order=order, created_by=user, updated_by=user, **item_data
            )
        return order

    def update(self, instance, validated_data):
        if "customer" in validated_data:
            validated_data.pop("customer")

        items_data = validated_data.pop("items", None)
        user = self.context["request"].user
        instance = self.assign_org_branch_on_update(instance, validated_data)

        # Update order fields
        branches = validated_data.pop("branches", None)
        validated_data.pop("organization", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user
        instance.save()

        if branches is not None:
            instance.branches.set(branches)

        if items_data is not None:
            existing_items = {item.id: item for item in instance.items.all()}
            updated_item_ids = []

            for item_data in items_data:
                item_id = item_data.get("id", None)
                item_data["updated_by"] = user

                if item_id and item_id in existing_items:
                    # Update existing item
                    item = existing_items[item_id]
                    for attr, value in item_data.items():
                        setattr(item, attr, value)
                    item.save()
                    updated_item_ids.append(item_id)
                else:
                    # Create new item
                    OrderItem.objects.create(
                        order=instance, created_by=user, updated_by=user, **item_data
                    )

            # Optionally: Delete removed items (not present in payload)
            for item_id, item in existing_items.items():
                if item_id not in updated_item_ids:
                    item.delete()

        return instance

    def validate(self, data):
        if self.instance is None:
            if not data.get("customer"):
                raise serializers.ValidationError({"customer": "Customer is required."})

        organization = data.get(
            "organization", getattr(self.instance, "organization", None)
        )
        branches = data.get("branches")

        if branches and not isinstance(branches, list):
            branches = list(branches.all())

        if organization and branches:
            invalid_branches = [
                branch
                for branch in branches
                if not self.branch_belongs_to_org(branch, organization)
            ]
            if invalid_branches:
                branch_names = ", ".join([b.name for b in invalid_branches])
                raise serializers.ValidationError(
                    f"The following branches do not belong to the organization '{organization.name}': {branch_names}"
                )
        return data

    def branch_belongs_to_org(self, branch, organization):
        return branch.parent == organization


class OrderDetailSerializer(OrderSerializer):
    customer_detail = CustomerSerializer(
        source="customer",
        read_only=True,
    )
    order_items = OrderItemSerializer(
        source="items",
        many=True,
        read_only=True,
    )
    order_payments = OrderPaymentSerializer(
        source="payments",
        many=True,
        read_only=True,
    )

    class Meta(OrderSerializer.Meta):
        fields = "__all__"


class UnpaidCreditOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    credit_used = serializers.SerializerMethodField()
    repaid_amount = serializers.SerializerMethodField()
    remaining_credit = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "customer_name",
            "total",
            "credit_used",
            "repaid_amount",
            "remaining_credit",
            "created_at",
        ]

    @extend_schema_field(serializers.CharField())
    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_credit_used(self, obj):
        return (
            obj.payments.filter(payment_type="credit").aggregate(
                total=Sum("received_amount")
            )["total"]
            or 0
        )

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_repaid_amount(self, obj):
        return (
            obj.payments.filter(payment_type="repayment").aggregate(
                total=Sum("received_amount")
            )["total"]
            or 0
        )

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=3))
    def get_remaining_credit(self, obj):
        credit = self.get_credit_used(obj)
        repaid = self.get_repaid_amount(obj)
        remaining = credit - repaid

        if abs(remaining) < 1:
            return 0

        return max(remaining, 0)
