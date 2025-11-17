from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import timedelta
import random
import string

# laundry model imports
from apps.organizations.models import Organization


# Create your models here.
class AuthUser(AbstractUser):
    address = models.TextField(blank=True, null=True)
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

    profile_picture = models.ImageField(
        upload_to="user_profiles/",
        null=True,
        blank=True,
        help_text="Upload a profile picture for the user",
    )

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

    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_users",
        help_text="The user who created this user record",
    )
    updated_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_users",
        help_text="The user who last updated this user record",
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

    created_by = models.ForeignKey(
        AuthUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="groupdetails_created",
        help_text="The user who created this group detail record",
    )
    updated_by = models.ForeignKey(
        AuthUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="groupdetails_updated",
        help_text="The user who last updated this group detail record",
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

# Password Reset model
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        AuthUser, on_delete=models.CASCADE, related_name="password_reset_otps"
    )
    otp_code = models.CharField(max_length=6, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if OTP is within 1 minutes and not used"""
        expiry_time = self.created_at + timedelta(minutes=10)
        return timezone.now() <= expiry_time and not self.is_used

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"

    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))