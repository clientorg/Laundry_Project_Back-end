from datetime import date

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from apps.licensing.models import AppliedLicense, apply_license_key
from apps.licensing.serializers import LicenseStatusSerializer, ApplyLicenseSerializer
from apps.accounts.models import AuthUser

from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin

from .models import License
from .serializers import LicenseSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["License"])
class LicenseStatusView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LicenseStatusSerializer

    def get(self, request):
        org = request.user.organization

        if not org:
            org = request.user.branches.first()

        root_org = org.parent if org and org.parent else org

        license_obj = (
            AppliedLicense.objects.filter(
                organization=root_org,
                is_active=True,
            )
            .order_by("-id")
            .first()
        )

        if not license_obj:
            return Response(
                {"detail": "No active license found."},
                status=404,
            )

        plan = root_org.subscriptions.order_by("-id").first().plan

        org_ids = list(root_org.branches.values_list("id", flat=True))
        org_ids.append(root_org.id)

        used_users = AuthUser.objects.filter(organization_id__in=org_ids).count()

        used_branches = root_org.branches.count()

        days_remaining = (license_obj.expires_on - date.today()).days

        data = {
            "company_name": license_obj.company_name,
            "plan_name": license_obj.plan_name,
            "max_users": plan.max_users,
            "used_users": used_users,
            "max_branches": plan.max_branches,
            "used_branches": used_branches,
            "expires_on": license_obj.expires_on,
            "days_remaining": max(days_remaining, 0),
            "status": "Active" if days_remaining >= 0 else "Expired",
        }

        serializer = LicenseStatusSerializer(data)

        return Response(serializer.data)


@extend_schema(tags=["License"])
class ApplyLicenseView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ApplyLicenseSerializer

    def post(self, request):
        serializer = ApplyLicenseSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["key"]

        try:
            apply_license_key(token)

            import apps.licensing.state as license_state

            license_state.LICENSE_VALID = True

            return Response(
                {"detail": "License applied successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=["License"])
class LicenseListCreateView(
    PermissionRequiredMixin,
    generics.ListCreateAPIView,
):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        HasAccessPermission,
    ]

    permission_map = {
        "GET": "licensing.view_license",
        "POST": "licensing.add_license",
    }

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only super administrators can create licenses.")

        serializer.save()
