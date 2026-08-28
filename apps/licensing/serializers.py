from datetime import date, timedelta

from rest_framework import serializers
from .models import License
from .service import sign_payload


class LicenseStatusSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    plan_name = serializers.CharField()
    max_users = serializers.IntegerField()
    used_users = serializers.IntegerField()
    max_branches = serializers.IntegerField()
    used_branches = serializers.IntegerField()
    expires_on = serializers.DateField()
    days_remaining = serializers.IntegerField()
    status = serializers.CharField()


class ApplyLicenseSerializer(serializers.Serializer):
    key = serializers.CharField()


class LicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = License
        fields = [
            "id",
            "license_id",
            "license_type",
            "company_name",
            "plan_name",
            "price",
            "max_branches",
            "max_users",
            "duration_days",
            "expires_on",
            "admin_username",
            "admin_name",
            "admin_email",
            "admin_password",
            "license_key",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "expires_on",
            "license_key",
            "created_at",
            "updated_at",
        ]

    def validate_duration_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0 days.")
        return value

    def validate(self, attrs):
        if attrs["license_type"] == License.ACTIVATION:
            required_fields = [
                "admin_username",
                "admin_name",
                "admin_email",
                "admin_password",
            ]

            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(
                        {field: "This field is required for activation licenses."}
                    )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        duration_days = validated_data["duration_days"]
        expires_on = date.today() + timedelta(days=duration_days)

        validated_data["expires_on"] = expires_on

        payload = {
            "type": validated_data["license_type"],
            "license_id": validated_data["license_id"],
            "company_name": validated_data["company_name"],
            "plan_name": validated_data["plan_name"],
            "price": float(validated_data["price"]),
            "max_branches": validated_data["max_branches"],
            "max_users": validated_data["max_users"],
            "duration_days": duration_days,
            "expires_on": expires_on.isoformat(),
        }

        if validated_data["license_type"] == License.ACTIVATION:
            payload.update(
                {
                    "admin_username": validated_data.get("admin_username"),
                    "admin_name": validated_data.get("admin_name"),
                    "admin_email": validated_data.get("admin_email"),
                    "admin_password": validated_data.get("admin_password"),
                }
            )

        license_key = sign_payload(payload)

        return License.objects.create(
            **validated_data,
            license_key=license_key,
            created_by=request.user,
        )
