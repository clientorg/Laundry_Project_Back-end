from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission

# laundry model imports
from apps.organizations.models import Organization


# Create your models here.
class AuthUser(AbstractUser):
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_users",
        help_text="The main/root organization of the user",
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="branch_users",
        help_text="Branches the user is allowed to access",
    )

    def __str__(self):
        return self.username


class GroupDetail(models.Model):
    description = models.TextField(blank=True)
    is_staff_only = models.BooleanField(default=False)

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="detail",
    )
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    branches = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="group_details",
    )

    def __str__(self):
        return f"Detail of Group: {self.group.name}"


class PermissionDetail(models.Model):
    permission = models.OneToOneField(
        Permission, on_delete=models.CASCADE, related_name="detail"
    )
    is_staff_only = models.BooleanField(default=False)

    def __str__(self):
        return f"Detail for {self.permission.codename}"
