# package imports
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# laundry model imports
from .models import Order, OrderItem

# laundry serializer imports
from apps.customers.serializers import CustomerSerializer


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


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
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
        order = Order.objects.create(created_by=user, updated_by=user, **validated_data)
        for item_data in items_data:
            OrderItem.objects.create(
                order=order, created_by=user, updated_by=user, **item_data
            )
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        user = self.context["request"].user

        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user
        instance.save()

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

    class Meta(OrderSerializer.Meta):
        fields = "__all__"
