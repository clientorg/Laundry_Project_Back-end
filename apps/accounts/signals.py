from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, Permission

# laundry model imports
from .models import GroupDetail, PermissionDetail


@receiver(post_save, sender=Group)
def create_group_detail(sender, instance, created, **kwargs):
    if created:
        GroupDetail.objects.create(group=instance)


@receiver(post_save, sender=Permission)
def create_permission_detail(sender, instance, created, **kwargs):
    if created:
        PermissionDetail.objects.create(permission=instance)
