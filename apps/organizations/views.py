# package imports
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied

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
        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Only super administrators can create organizations."
            )
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

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Only super administrators can delete organizations."
            )

        instance.delete()


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

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Only super administrators can create plans."
            )

        serializer.save()


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

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Only super administrators can update plans."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Only super administrators can delete plans."
            )

        instance.delete()

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
        if not request.user.is_superuser:
            raise PermissionDenied(
                "Only super administrators can change an organization's plan."
            )

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

# --------------- Organization Setup View ---------------#
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from apps.accounts.models import GroupDetail
from apps.organizations.models import Plan, Organization, OrganizationSubscription
from apps.organizations.serializers import OrganizationSetupSerializer

User = get_user_model()

@extend_schema(
    tags=["Organizations"],
    request=OrganizationSetupSerializer,
    description="Setup a new Organization with Plan, Subscription, and Admin User.",
    summary="Organization Setup (Plan + Org + Subscription + User)"
)

class OrganizationSetupView(APIView):
    def post(self, request):
        serializer = OrganizationSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_data = serializer.validated_data["plan"]
        org_data = serializer.validated_data["organization"]
        user_data = serializer.validated_data["user"]

        try:
            with transaction.atomic():
                # 1. Create User first (no org yet)
                user = User.objects.create(
                    username=user_data["username"],
                    password=make_password(user_data["password"])
                )

                # 2. Create Plan
                plan = Plan.objects.create(
                    name=plan_data["name"],
                    description=plan_data.get("description", ""),
                    price=plan_data["price"],
                    max_users=plan_data.get("max_users", 1),  # optional
                    max_branches=plan_data["max_branches"],
                    duration_days=plan_data["duration_days"],
                )

                # 3. Create Organization (root)
                organization = Organization.objects.create(
                    name=org_data["name"],
                    created_by=user,
                    updated_by=user,
                    parent=None
                )
                # SIGNALS WILL EXECUTE HERE 

                # 4. Create Subscription
                subscription = OrganizationSubscription.objects.create(
                    organization=organization,
                    plan=plan
                )

                # 5. Assign user to org + OrgAdmin group
                user.organization = organization
                user.save()

                # find the OrgAdmin group created by signal automation
                orgadmin_group_detail = GroupDetail.objects.filter(
                    organization=organization,
                    group__name__startswith="org_admin_"
                ).first()

                if not orgadmin_group_detail:
                    return Response(
                        {"detail": "OrgAdmin group not found after automation."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                orgadmin_group_detail.group.user_set.add(user)

                # Success Response
                return Response(
                    {
                        "message": "Organization setup completed successfully.",
                        "organization": {
                            "id": organization.id,
                            "name": organization.name
                        },
                        "plan": {
                            "id": plan.id,
                            "name": plan.name
                        },
                        "subscription": {
                            "started_at": subscription.started_at,
                            "expires_at": subscription.expires_at
                        },
                        "user": {
                            "id": user.id,
                            "username": user.username
                        }
                    },
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
