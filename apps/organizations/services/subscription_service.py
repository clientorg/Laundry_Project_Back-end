from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from apps.organizations.models import (
    OrganizationSubscription,
    Organization,
)


# Service to get active subscription
def get_active_subscription(organization):
    """
    Returns the currently active subscription for the organization.
    Rule:
    - subscription.is_active == True
    - if multiple, return the latest one (by started_at)
    """
    now = timezone.now()

    return (
        OrganizationSubscription.objects
        .filter(
            organization=organization,
            started_at__lte=now,
            expires_at__gte=now,
        )
        .order_by("-started_at")
        .first()
    )

# Branch limit exception
class BranchLimitExceeded(Exception):
    """
    Raised when an organization tries to exceed its plan's branch limit.
    """
    pass

# Service to check branch limit
def check_branch_limit(organization):
    """
    Checks whether the organization can create a new branch
    under its current active subscription.

    Raises:
        BranchLimitExceeded: if branch limit is reached
    """

    subscription = get_active_subscription(organization)

    if not subscription:
        raise BranchLimitExceeded(
            "No active subscription found for this organization."
        )

    max_branches = subscription.plan.max_branches

    current_branch_count = Organization.objects.filter(
        parent=organization
    ).count()

    if current_branch_count >= max_branches:
        raise BranchLimitExceeded(
            f"Branch limit reached. "
            f"Current plan allows only {max_branches} branches."
        )

    return True


class PlanDowngradeNotAllowed(Exception):
    """
    Raised when attempting to downgrade to a plan
    that allows fewer branches than currently exist.
    """
    pass


# Service to change organization plan
def change_organization_plan(organization, new_plan):
    """
    Changes the organization's plan immediately.

    Behavior:
    - If downgrading and current branches exceed new plan limit → BLOCK
    - Ends the current active subscription (if any) at now
    - Starts a new subscription immediately
    """

    now = timezone.now()

    #DOWNGRADE SAFETY CHECK (D1)
    current_branch_count = Organization.objects.filter(
        parent=organization
    ).count()

    if current_branch_count > new_plan.max_branches:
        raise PlanDowngradeNotAllowed(
            f"Cannot switch to plan '{new_plan.name}'. "
            f"Current branches: {current_branch_count}, "
            f"but this plan allows only {new_plan.max_branches}. "
            f"Please reduce branches before downgrading."
        )

    #End current active subscription (if exists)
    active_sub = get_active_subscription(organization)
    if active_sub:
        active_sub.expires_at = now
        active_sub.save(update_fields=["expires_at"])

    #Create new subscription starting now
    new_subscription = OrganizationSubscription.objects.create(
        organization=organization,
        plan=new_plan,
        started_at=now,
        expires_at=now + timedelta(days=new_plan.duration_days),
    )

    return new_subscription