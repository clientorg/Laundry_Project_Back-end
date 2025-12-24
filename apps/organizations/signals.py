import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, Permission

# laundry model imports
from apps.accounts.models import GroupDetail, PermissionDetail


from .models import Organization
from apps.master.models import Item, ServiceType, HandlingType, DeliveryType

# AUTO CREATE GROUPS & PERMISSIONS
def create_default_groups_for_org(user, organization):
    """
    Create four groups for this organization and assign permissions:
      - OrgAdmin: ALL perms EXCEPT organizations.add_organization and organizations.delete_organization
      - Admin, Manager, Staff: ALL perms EXCEPT user/group/branch/permission/organization management
    """

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    GROUPS = {
        "OrgAdmin": f"org_admin_{timestamp}",
        "Admin": f"admin_{timestamp}",
        "Manager": f"manager_{timestamp}",
        "Staff": f"staff_{timestamp}",
    }

    groups_map = {}

    # Create groups with unique timestamp names
    for key, group_name in GROUPS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        groups_map[key] = group

        # Ensure GroupDetail is created/updated correctly
        gd, _ = GroupDetail.objects.get_or_create(group=group)
        gd.organization = organization
        gd.description = f"{group_name} for {organization.name}"
        gd.created_by = user
        gd.updated_by = user
        gd.save()

    # permissions to exclude
    orgadmin_exclude = {"add_organization", "delete_organization"}
    admin_exclude = {
        # user management (accounts app likely uses 'authuser' or 'user' codename; we exclude generic codenames)
        "add_authuser", "change_authuser", "delete_authuser", "view_authuser",
        "add_group", "change_group", "delete_group", "view_group",
        "add_branch", "change_branch", "delete_branch", "view_branch",  # if branch perms exist
        "add_permission", "change_permission", "delete_permission", "view_permission",
        "add_organization", "change_organization", "delete_organization", "view_organization",
    }

    # iterate all permissions and assign respecting exclusions
    all_perms = Permission.objects.all()
    for perm in all_perms:
        codename = perm.codename 

        # OrgAdmin: all except org create/delete
        if codename not in orgadmin_exclude:
            groups_map["OrgAdmin"].permissions.add(perm)

        # Admin / Manager / Staff: all except admin_exclude set
        if codename not in admin_exclude:
            groups_map["Admin"].permissions.add(perm)
            groups_map["Manager"].permissions.add(perm)
            groups_map["Staff"].permissions.add(perm)

        # ensure PermissionDetail exists for this permission
        PermissionDetail.objects.get_or_create(permission=perm)

    # assign the new user to OrgAdmin by default
    user.groups.add(groups_map["OrgAdmin"])


def create_default_master_data_for_org(user, organization):
    """
    Create default Items, ServiceType, HandlingType and DeliveryType
    for the new organization.
    """

    DEFAULT_ITEMS = [
        "Abaya",
        "Carpet or Rugs",
        "Shirt",
        "Pant",
        "Towel",
        "Blanket",
        "Jacket",
    ]

    for idx, name in enumerate(DEFAULT_ITEMS):
        Item.objects.get_or_create(
            name=name,
            organization=organization,
            defaults={
                "secondary_name": "",
                "description": "",
                "is_pinned": True if idx < 6 else False,  # first 6 pinned
                "is_global": True,
                "is_size_based_price": True
                if name == "Carpet or Rugs"
                else False,
                "extra_data": {
                    "Laundry": {
                        "price": 2,
                        "enabled": True,
                    }
                }
                if name == "Carpet or Rugs"
                else {},
                "created_by": user,
                "updated_by": user,
            },
        )

    DEFAULT_SERVICE_TYPES = ["Dry Clean", "Laundry", "Pressing", "Steam"]
    for name in DEFAULT_SERVICE_TYPES:
        ServiceType.objects.get_or_create(
            name=name,
            organization=organization,
            defaults={
                "is_global": True,
                "created_by": user,
                "updated_by": user,
            },
        )

    DEFAULT_HANDLING_TYPES = ["Folding", "Hangered"]
    for name in DEFAULT_HANDLING_TYPES:
        HandlingType.objects.get_or_create(
            name=name,
            organization=organization,
            defaults={
                "is_global": True,
                "created_by": user,
                "updated_by": user,
            },
        )

    DEFAULT_DELIVERY_TYPES = ["Normal", "Express"]
    for name in DEFAULT_DELIVERY_TYPES:
        DeliveryType.objects.get_or_create(
            name=name,
            organization=organization,
            defaults={
                "is_global": True,
                "created_by": user,
                "updated_by": user,
            },
        )

@receiver(post_save, sender=Organization)
def organization_post_create(sender, instance, created, **kwargs):
    """
    Root Organization automation entry point.
    """

    # Run only on creation
    if not created:
        return

    # Run only for ROOT organizations
    if instance.parent is not None:
        return

    # Actor = user who created the organization
    actor = instance.created_by
    if not actor:
        return

    # ---- Automation calls will go here ----
    create_default_groups_for_org(actor, instance)
    create_default_master_data_for_org(actor, instance)