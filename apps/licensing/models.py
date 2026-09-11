from django.db import models
from datetime import date, datetime
from django.contrib.auth import get_user_model

from apps.licensing.utils import verify_license

from apps.accounts.models import AuthUser
from django.contrib.auth.models import Group
from apps.organizations.models import (
    Organization,
    Plan,
    OrganizationSubscription,
)

User = get_user_model()


# Create your models here.
class AppliedLicense(models.Model):
    license_id = models.CharField(
        max_length=100,
        unique=True,
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="licenses",
    )

    raw_key = models.TextField()

    company_name = models.CharField(
        max_length=255,
    )

    plan_name = models.CharField(
        max_length=100,
    )

    applied_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_on = models.DateField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.company_name} - {self.plan_name}"


def apply_license_key(token):
    payload = verify_license(token)

    if AppliedLicense.objects.filter(raw_key=token).exists():
        raise Exception("This license key was already used.")

    expiry = datetime.strptime(
        payload["expires_on"],
        "%Y-%m-%d",
    ).date()

    if expiry < date.today():
        raise Exception("License key expired.")

    license_type = payload.get("type", "activation").lower()

    # SYSTEM USER
    system_user = AuthUser.objects.filter(is_superuser=True).first()

    if not system_user:
        raise Exception("System admin user not found.")

    # ORGANIZATION MUST EXIST FOR RENEWAL
    organization = Organization.objects.filter(
        name=payload["company_name"],
        parent=None,
    ).first()

    # ACTIVATION FLOW
    if license_type == "activation":

        if organization:
            raise Exception("Organization already exists. Use renewal key.")

        organization = Organization.objects.create(
            name=payload["company_name"],
            created_by=system_user,
            updated_by=system_user,
        )

        user, created = AuthUser.objects.get_or_create(
            username=payload["admin_username"],
            organization=organization,
            defaults={
                "email": payload["admin_email"],
                "first_name": payload["admin_name"],
                "is_staff": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(payload["admin_password"])
            user.save()

        org_admin = Group.objects.filter(
            detail__organization=organization,
            name__icontains="org_admin",
        ).first()

        if org_admin:
            user.groups.add(org_admin)

    # RENEWAL FLOW
    elif license_type == "renewal":

        if not organization:
            raise Exception("Organization not found. Use activation key first.")

    else:
        raise Exception("Invalid license type.")

    # PLAN CREATE / UPDATE
    plan, _ = Plan.objects.get_or_create(
        name=payload["plan_name"],
        defaults={
            "description": f"{payload['plan_name']} Plan",
            "price": payload["price"],
            "max_users": payload["max_users"],
            "max_branches": payload["max_branches"],
            "duration_days": payload["duration_days"],
        },
    )

    # DEACTIVATE OLD LICENSES
    AppliedLicense.objects.filter(
        organization=organization,
        is_active=True,
    ).update(is_active=False)

    # NEW SUBSCRIPTION
    OrganizationSubscription.objects.create(
        organization=organization,
        plan=plan,
    )

    # STORE APPLIED LICENSE
    AppliedLicense.objects.create(
        license_id=payload["license_id"],
        organization=organization,
        raw_key=token,
        company_name=payload["company_name"],
        plan_name=payload["plan_name"],
        expires_on=payload["expires_on"],
        is_active=True,
    )

    return organization


class License(models.Model):
    ACTIVATION = "activation"
    RENEWAL = "renewal"

    LICENSE_TYPE_CHOICES = [
        (ACTIVATION, "Activation"),
        (RENEWAL, "Renewal"),
    ]

    license_id = models.CharField(max_length=100, unique=True)
    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPE_CHOICES,
    )

    company_name = models.CharField(max_length=255)
    plan_name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
    )

    max_branches = models.PositiveIntegerField(default=1)
    max_users = models.PositiveIntegerField(default=5)
    duration_days = models.PositiveIntegerField()

    expires_on = models.DateField()

    admin_username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    admin_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    admin_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    admin_email = models.EmailField(
        blank=True,
        null=True,
    )

    license_key = models.TextField(
        blank=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="licenses_created",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.license_id} - {self.company_name}"
