from django.db import models
from django.core.exceptions import FieldDoesNotExist


class OrgBranchAssignMixin:
    """
    Handles automatic assignment of organization/branches
    during create & update based on request.user.
    """

    def assign_org_branch_on_create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        has_org = "organization" in validated_data and validated_data["organization"]
        has_branches = "branches" in validated_data and validated_data["branches"]

        if not has_org and not has_branches:
            if user and user.organization:
                validated_data["organization"] = user.organization
                validated_data["branches"] = []
            elif user and user.branches.exists():
                branch = user.branches.first()
                validated_data["organization"] = None
                validated_data["branches"] = [branch]
            else:
                validated_data["organization"] = None
                validated_data["branches"] = []

        return validated_data

    def assign_org_branch_on_update(self, instance, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        has_org = "organization" in validated_data and validated_data["organization"]
        has_branches = "branches" in validated_data and validated_data["branches"]

        # Handle organization
        if has_org:
            instance.organization = validated_data["organization"]
        elif not instance.organization and user and user.organization:
            instance.organization = user.organization

        # Handle branches
        if has_branches:
            instance.branches.set(validated_data["branches"])
        elif not instance.branches.exists() and user and user.branches.exists():
            instance.branches.set([user.branches.first()])
        return instance


class OrgBranchQuerysetMixin:
    """
    Restrict queryset results based on the user's organization or branches.

    - If the user has an organization → include that org and its branches.
    - If the user only has branches → include those branches (+ global items if model has is_global).
    - If neither → return empty queryset.
    """

    org_field = "organization"  # ForeignKey to Organization
    branch_field = "branches"  # ManyToMany to Organization

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        model = qs.model

        if user.organization:
            return qs.filter(
                models.Q(**{self.org_field: user.organization})
                | models.Q(**{f"{self.branch_field}__parent": user.organization})
            ).distinct()

        elif user.branches.exists():
            filters = models.Q(**{f"{self.branch_field}__in": user.branches.all()})

            # Add is_global=True only if the model has that field
            try:
                model._meta.get_field("is_global")
                filters |= models.Q(is_global=True) & (
                    models.Q(**{self.org_field: user.organization})
                    | models.Q(**{f"{self.branch_field}__parent": user.organization})
                )
            except FieldDoesNotExist:
                pass

            return qs.filter(filters).distinct()

        return qs.none()


class BranchQuerysetMixin:
    """Restricts branches based on the user's organization or branch membership."""

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.organization:
            # User belongs to an org → fetch its branches
            return qs.filter(parent=user.organization)

        elif user.branches.exists():
            # User belongs only to a branch → restrict to their branch
            return qs.filter(id__in=user.branches.values_list("id", flat=True))

        return qs.none()
