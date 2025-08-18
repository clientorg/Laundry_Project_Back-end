from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import AuthUser, GroupDetail, PermissionDetail
from apps.organizations.models import Organization

# Register your models here.
admin.site.unregister(Group)


class GroupDetailForm(forms.ModelForm):
    class Meta:
        model = GroupDetail
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only root organizations
        self.fields["organization"].queryset = Organization.objects.filter(
            parent__isnull=True
        )
        # Only branches
        self.fields["branches"].queryset = Organization.objects.filter(
            parent__isnull=False
        )


class GroupDetailInline(admin.StackedInline):
    model = GroupDetail
    form = GroupDetailForm
    can_delete = False
    verbose_name_plural = "Group Details"
    filter_horizontal = ("branches",)


class PermissionDetailInline(admin.StackedInline):
    model = PermissionDetail
    can_delete = False


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Organization & Branches", {"fields": ("organization", "branches")}),
        (
            "Contact Information",
            {"fields": ("address", "country_code", "mobile_number", "profile_picture")},
        ),
    )
    list_display = UserAdmin.list_display + (
        "is_super_admin",
        "organization_name",
        "branches_count",
        "mobile_number",
        "country_code",
        "profile_picture_preview",  # 👈 show small preview
    )

    filter_horizontal = ("groups", "user_permissions", "branches")

    def organization_name(self, obj):
        return obj.organization.name if obj.organization else "-"

    organization_name.short_description = "Organization"

    def branches_count(self, obj):
        return obj.branches.count()

    branches_count.short_description = "Branches Count"

    def is_super_admin(self, obj):
        if hasattr(obj, "is_superuser"):
            return obj.is_superuser
        return False

    is_super_admin.boolean = True
    is_super_admin.short_description = "Super User Status"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "branches":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # 👇 Add preview in list view
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.profile_picture.url,
            )
        return "-"

    profile_picture_preview.short_description = "Profile Picture"


@admin.register(Group)
class AuthGroupAdmin(GroupAdmin):
    inlines = [GroupDetailInline]
    list_display = (
        "name",
        "organization_name",
        "branches_count",
        "is_staff_only",
    )

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def organization_name(self, obj):
        return obj.detail.organization.name if obj.detail.organization else "-"

    organization_name.short_description = "Organization"

    def branches_count(self, obj):
        return obj.detail.branches.count()

    branches_count.short_description = "Branches Count"

    def is_staff_only(self, obj):
        if hasattr(obj, "detail") and hasattr(obj.detail, "is_staff_only"):
            return obj.detail.is_staff_only
        return False

    is_staff_only.boolean = True


@admin.register(Permission)
class AuthPermissionAdmin(admin.ModelAdmin):
    inlines = [PermissionDetailInline]
    list_display = (
        "name",
        "content_type",
        "is_staff_only",
    )

    def is_staff_only(self, obj):
        if hasattr(obj, "detail") and hasattr(obj.detail, "is_staff_only"):
            return obj.detail.is_staff_only
        return False

    is_staff_only.boolean = True
