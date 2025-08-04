from rest_framework import permissions
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
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
        self.required_permission = self.get_required_permission()
        super().initial(request, *args, **kwargs)
