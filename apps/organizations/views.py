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
        "GET": ["organizations.view_branch", "orders.view_order"],
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


#--------------- Organization Views ---------------#
from .models import Organization
from .serializers import OrganizationSerializer


@extend_schema(tags=["Organizations"])
class OrganizationListCreateView(
    PermissionRequiredMixin, generics.ListCreateAPIView
):
    queryset = Organization.objects.filter(parent__isnull=True)
    serializer_class = OrganizationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": ["organizations.view_organization", "orders.view_order"],
        "POST": "organizations.add_organization",
    }

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def perform_create(self, serializer):
        serializer.save()

@extend_schema(tags=["Organizations"])
class OrganizationRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Organization.objects.filter(parent__isnull=True)
    serializer_class = OrganizationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "organizations.view_organization",
        "PUT": "organizations.change_organization",
        "PATCH": "organizations.change_organization",
        "DELETE": "organizations.delete_organization",
    }

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# --------------- Plan Views ---------------#
from apps.organizations.models import Plan
from apps.organizations.serializers import PlanSerializer


@extend_schema(tags=["Plans"])
class PlanListCreateView(
    PermissionRequiredMixin, generics.ListCreateAPIView
):
    queryset = Plan.objects.all().order_by("id")
    serializer_class = PlanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "organizations.view_plan",
        "POST": "organizations.add_plan",
    }


@extend_schema(tags=["Plans"])
class PlanRetrieveUpdateDestroyView(
    PermissionRequiredMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "organizations.view_plan",
        "PUT": "organizations.change_plan",
        "PATCH": "organizations.change_plan",
        "DELETE": "organizations.delete_plan",
    }

#--------------- Change Organization Plan View ---------------#
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.organizations.models import Plan
from apps.organizations.serializers import ChangePlanSerializer
from apps.organizations.services.subscription_service import (
    change_organization_plan,
    PlanDowngradeNotAllowed,
    get_active_subscription
)
from rest_framework.permissions import IsAuthenticated

@extend_schema(
    tags=["Organizations"],
    request=ChangePlanSerializer, 
)
class OrganizationChangePlanView(PermissionRequiredMixin, APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasAccessPermission]

    permission_map = {
        "POST": "organizations.change_organization",
    }

    def post(self, request, pk):
        serializer = ChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = get_object_or_404(
            Organization,
            pk=pk,
            parent__isnull=True
        )

        plan = get_object_or_404(
            Plan,
            pk=serializer.validated_data["plan_id"]
        )

        #prevent duplicate first subscription
        active_subscription = get_active_subscription(organization)

        try:
            subscription = change_organization_plan(organization, plan)
        except PlanDowngradeNotAllowed as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": (
                    "Subscription created successfully."
                    if not active_subscription
                    else "Plan changed successfully."
                ),
                "plan": plan.name,
                "started_at": subscription.started_at,
                "expires_at": subscription.expires_at,
            },
            status=status.HTTP_200_OK,
        )
