from django.db import models

# laundry model imports
from .models import GroupDetail


class GroupOrgBranchAssignMixin:
    """
    Handles automatic assignment of organization/branches
    for Group -> GroupDetail during create & update,
    including created_by and updated_by.
    """

    def assign_org_branch_on_create(self, group, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # Get or create the GroupDetail for this group
        detail_data = validated_data.pop("detail", {})
        detail, created = GroupDetail.objects.get_or_create(group=group)

        # If request body does not already specify org/branches
        if not detail_data.get("organization") and not detail_data.get("branches"):
            if user and user.organization:
                detail.organization = user.organization
                detail.branches.clear()
            elif user and user.branches.exists():
                detail.organization = None
                detail.branches.set([user.branches.first()])
            else:
                detail.organization = None
                detail.branches.clear()
        else:
            # Respect request data
            if "organization" in detail_data:
                detail.organization = detail_data["organization"]
            if "branches" in detail_data:
                detail.branches.set(detail_data["branches"])

        for field, value in detail_data.items():
            if field not in ["organization", "branches"]:  # already handled above
                setattr(detail, field, value)

        # Audit fields
        if not created:  # only set on first create
            detail.created_by = user
        detail.updated_by = user

        detail.save()
        return group

    def assign_org_branch_on_update(self, group, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        detail_data = validated_data.pop("detail", {})
        detail, _ = GroupDetail.objects.get_or_create(group=group)

        if "organization" in detail_data:
            detail.organization = detail_data["organization"]
        elif not detail.organization and user and user.organization:
            detail.organization = user.organization

        if "branches" in detail_data:
            detail.branches.set(detail_data["branches"])
        elif not detail.branches.exists() and user and user.branches.exists():
            detail.branches.set([user.branches.first()])

        for field, value in detail_data.items():
            if field not in ["organization", "branches"]:  # already handled above
                setattr(detail, field, value)

        # Audit fields
        if not detail.created_by:
            detail.created_by = user  # fallback if missing
        detail.updated_by = user

        detail.save()
        return group


class GroupOrgBranchQuerysetMixin:
    """
    Restricts Group queryset based on user's organization/branches.

    - If user has an organization → include groups with that org in GroupDetail,
      plus groups linked to its branches.
    - If user only has branches → include groups with those branches in GroupDetail,
      and also include is_global groups if you plan to add that later.
    """

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related("detail")

        if user.organization:
            return qs.filter(
                models.Q(detail__organization=user.organization)
                | models.Q(detail__branches__parent=user.organization)
            ).distinct()

        elif user.branches.exists():
            return qs.filter(detail__branches__in=user.branches.all()).distinct()

        return qs.none()
