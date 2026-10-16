from rest_framework import permissions
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from rest_framework.exceptions import PermissionDenied
from .models import PermissionDetail


class HasAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(
            view,
            "required_permission",
            None,
        )

        if not required_permission:
            return True
        if not request.user.is_authenticated:
            return False

        try:
            codename = required_permission.split(".")[-1]
            perm = Permission.objects.get(codename=codename)
            if hasattr(perm, "detail") and perm.detail.is_staff_only:
                return False
        except Permission.DoesNotExist:
            return False

        return request.user.has_perm(required_permission)


class PermissionRequiredMixin(APIView):
    permission_map = {}

    def get_required_permission(self):
        return self.permission_map.get(self.request.method)

    def initial(self, request, *args, **kwargs):
        required_perms = self.get_required_permission()

        # allow None → no validation
        if required_perms:
            if isinstance(required_perms, str):
                required_perms = [required_perms]  # convert to list

            # user must have at least one of the permissions
            if not any(request.user.has_perm(perm) for perm in required_perms):
                raise PermissionDenied(
                    f"Requires one of these permissions: {', '.join(required_perms)}"
                )

        super().initial(request, *args, **kwargs)
