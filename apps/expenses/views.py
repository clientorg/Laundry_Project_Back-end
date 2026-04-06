from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin
from apps.organizations.mixins import OrgBranchQuerysetMixin

from .models import ExpenseCategory, Expense
from .serializers import ExpenseCategorySerializer, ExpenseSerializer


@extend_schema_view(
    list=extend_schema(summary="List Expense Categories", tags=["Expenses: Category"]),
    create=extend_schema(summary="Create Expense Category", tags=["Expenses: Category"]),
    retrieve=extend_schema(summary="Get Expense Category", tags=["Expenses: Category"]),
    update=extend_schema(summary="Update Expense Category", tags=["Expenses: Category"]),
    partial_update=extend_schema(summary="Patch Expense Category", tags=["Expenses: Category"]),
    destroy=extend_schema(summary="Delete Expense Category", tags=["Expenses: Category"]),
)
class ExpenseCategoryViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all().order_by("-id")
    serializer_class = ExpenseCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "expenses.view_expensecategory",
        "POST": "expenses.add_expensecategory",
        "PUT": "expenses.change_expensecategory",
        "PATCH": "expenses.change_expensecategory",
        "DELETE": "expenses.delete_expensecategory",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List Expenses", tags=["Expenses"]),
    create=extend_schema(summary="Create Expense", tags=["Expenses"]),
    retrieve=extend_schema(summary="Get Expense", tags=["Expenses"]),
    update=extend_schema(summary="Update Expense", tags=["Expenses"]),
    partial_update=extend_schema(summary="Patch Expense", tags=["Expenses"]),
    destroy=extend_schema(summary="Delete Expense", tags=["Expenses"]),
)
class ExpenseViewSet(PermissionRequiredMixin, OrgBranchQuerysetMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by("-expense_date", "-created_at")
    serializer_class = ExpenseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {
        "GET": "expenses.view_expense",
        "POST": "expenses.add_expense",
        "PUT": "expenses.change_expense",
        "PATCH": "expenses.change_expense",
        "DELETE": "expenses.delete_expense",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        category_id = self.request.query_params.get("category")
        if from_date:
            qs = qs.filter(expense_date__gte=from_date)
        if to_date:
            qs = qs.filter(expense_date__lte=to_date)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
