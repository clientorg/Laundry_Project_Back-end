from django.urls import path

# package imports
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# laundry view imports
from .views import (
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    PermissionView,
    GroupListCreateView,
    GroupRetrieveUpdateDestroyView,
    GroupAssignedPermissionsView,
    GroupUnassignedPermissionsView,
    LoginAPIView,
    UserTokenDetailAPIView,
    RequestPasswordResetOTPView,
    ResetPasswordWithOTPView,
    ForgotUsernameView,
    ChangePasswordView,
)

urlpatterns = [
    path(
        "permissions/",
        PermissionView.as_view(),
        name="permissions",
    ),
    path("groups/", GroupListCreateView.as_view(), name="group-list-create"),
    path(
        "groups/<int:pk>/",
        GroupRetrieveUpdateDestroyView.as_view(),
        name="group-detail",
    ),
    path(
        "groups/<int:pk>/permissions/assigned/",
        GroupAssignedPermissionsView.as_view(),
        name="group-permissions",
    ),
    path(
        "groups/<int:pk>/permissions/unassigned/",
        GroupUnassignedPermissionsView.as_view(),
        name="group-permissions",
    ),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token-details/", UserTokenDetailAPIView.as_view(), name="user-token-detail"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path(
        "users/<int:pk>/", UserRetrieveUpdateDestroyView.as_view(), name="user-detail"
    ),

    #Password Reset via OTP
    path("password-reset/request-otp/", RequestPasswordResetOTPView.as_view(), name="request_password_reset_otp"),
    path("password-reset/reset/", ResetPasswordWithOTPView.as_view(), name="reset_password_with_otp"),
    path("password-reset/forgot-username/", ForgotUsernameView.as_view(), name="forgot_username"),

    #Change Password (requires authentication)
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
