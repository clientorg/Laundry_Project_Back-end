from django.shortcuts import render
from rest_framework import generics
from .models import Customer
from .serializers import CustomerSerializer


# Create your views here.
class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer


class CustomerDeleteView(generics.DestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerByUserView(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Customer.objects.filter(user_id=user_id).order_by("-created_at")


class CustomerUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = "pk"
