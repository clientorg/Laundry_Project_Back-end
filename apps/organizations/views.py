# package imports
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema

# laundry mixin imports
from .mixins import BranchQuerysetMixin

# laundry permission validator
from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

# laundry model imports
from .models import Branch

# laundry serializer imports
from .serializers import BranchSerializer


# branch views
@extend_schema(tags=["Branches"])
class BranchListCreateView(
    PermissionRequiredMixin, BranchQuerysetMixin, generics.ListCreateAPIView
):
    queryset = Branch.objects.exclude(parent=None)
    serializer_class = BranchSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "organizations.view_branch",
        "POST": "organizations.add_branch",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("name")


@extend_schema(tags=["Branches"])
class BranchRetrieveUpdateDestroyView(
    PermissionRequiredMixin, BranchQuerysetMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Branch.objects.exclude(parent=None)
    serializer_class = BranchSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "organizations.view_branch",
        "PUT": "organizations.change_branch",
        "PATCH": "organizations.change_branch",
        "DELETE": "organizations.delete_branch",
    }
