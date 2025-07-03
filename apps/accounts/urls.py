from django.urls import path

# package imports
from rest_framework_simplejwt.views import TokenRefreshView

# laundry view imports
from .views import LoginAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
