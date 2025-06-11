from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission
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

    def clean(self):
        cleaned_data = super().clean()

        if not self.pk:
            return cleaned_data

        if self.organization and self.branches.exists():
            invalid_branches = self.branches.exclude(parent=self.organization)
            if invalid_branches.exists():
                raise ValidationError(
                    "All selected branches must belong to the selected organization."
                )
        elif not self.organization and self.branches.exists():
            invalid_branches = self.branches.filter(parent__isnull=False)
            if invalid_branches.exists():
                raise ValidationError(
                    "Branches must not be linked when no organization is set."
                )

        if (self.organization or self.branches.exists()) and self.groups.exists():
            valid_org_ids = list(self.branches.values_list("id", flat=True))
            if self.organization:
                valid_org_ids.append(self.organization.id)

            invalid_groups = (
                self.groups.exclude(detail__organization__id__in=valid_org_ids)
                .exclude(detail__branches__id__in=valid_org_ids)
                .distinct()
            )

            if invalid_groups.exists():
                raise ValidationError(
                    "Some groups are not associated with the selected organization or branches."
                )

        return cleaned_data

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if self.organization and self.branches.exists():
            invalid_branches = self.branches.exclude(parent=self.organization)
            if invalid_branches.exists():
                raise ValidationError(
                    "All selected branches must belong to the selected organization."
                )
        elif not self.organization and self.branches.exists():
            invalid_branches = self.branches.filter(parent__isnull=False)
            if invalid_branches.exists():
                raise ValidationError(
                    "Branches must not be linked when no organization is set."
                )

        if (self.organization or self.branches.exists()) and self.groups.exists():
            valid_org_ids = list(self.branches.values_list("id", flat=True))
            if self.organization:
                valid_org_ids.append(self.organization.id)

            invalid_groups = (
                self.groups.exclude(detail__organization__id__in=valid_org_ids)
                .exclude(detail__branches__id__in=valid_org_ids)
                .distinct()
            )

            if invalid_groups.exists():
                raise ValidationError(
                    "Some groups are not associated with the selected organization or branches."
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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if self.organization and self.branches.exists():
            invalid_branches = self.branches.exclude(parent=self.organization)
            if invalid_branches.exists():
                raise ValidationError(
                    "All selected branches must belong to the selected organization."
                )
        elif not self.organization and self.branches.exists():
            invalid_branches = self.branches.filter(parent__isnull=True)
            if invalid_branches.exists():
                raise ValidationError("Branches must have a parent organization.")

    def __str__(self):
        return f"Detail of Group: {self.group.name}"


class PermissionDetail(models.Model):
    permission = models.OneToOneField(
        Permission, on_delete=models.CASCADE, related_name="detail"
    )
    is_staff_only = models.BooleanField(default=False)

    def __str__(self):
        return f"Detail for {self.permission.codename}"
