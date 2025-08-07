# package imports
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema

# laundry model imports
from .models import Branch

# laundry serializer imports
from .serializers import BranchSerializer


# branch views
@extend_schema(tags=["Branches"])
class BranchListCreateView(generics.ListCreateAPIView):
    queryset = Branch.objects.exclude(parent=None).order_by("name")
    serializer_class = BranchSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Branches"])
class BranchRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.exclude(parent=None)
    serializer_class = BranchSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
