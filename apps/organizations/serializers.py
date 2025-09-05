# package imports
from rest_framework import serializers

# laundry model imports
from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "description",
            "currency_code",
            "service_vat_percent",
            "address",
            "contact_name",
            "contact_mobile_number",
            "contact_email",
            "country",
            "country_code",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        parent = None

        if user.organization:
            parent = user.organization
        elif user.branches.exists():
            branch = user.branches.first()
            parent = branch.parent

        if not parent:
            raise serializers.ValidationError(
                "Unable to determine parent organization from user."
            )

        return Branch.objects.create(
            parent=parent,
            created_by=user,
            updated_by=user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        request = self.context["request"]
        user = request.user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = user
        instance.save()
        return instance
