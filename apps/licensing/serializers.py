from rest_framework import serializers


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
