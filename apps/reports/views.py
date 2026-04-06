from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDate, Coalesce
from django.db.models import DecimalField, ExpressionWrapper

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.accounts.permissions import HasAccessPermission, PermissionRequiredMixin
from apps.organizations.mixins import OrgBranchQuerysetMixin
from apps.orders.models import Order, OrderPayment
from apps.customers.models import Customer
from apps.expenses.models import Expense


def _parse_date(value, fallback):
    if not value:
        return fallback
    try:
        from datetime import datetime
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return fallback


def _filter_by_org_branch(qs, user, org_field="organization", branch_field="branches"):
    """Replicates OrgBranchQuerysetMixin logic for raw querysets."""
    if user.organization:
        return qs.filter(
            Q(**{org_field: user.organization})
            | Q(**{f"{branch_field}__parent": user.organization})
        ).distinct()
    elif user.branches.exists():
        return qs.filter(**{f"{branch_field}__in": user.branches.all()}).distinct()
    return qs.none()


# ----------------------------- Dashboard KPIs --------------------------------

@extend_schema(
    tags=["Reports: Dashboard"],
    summary="Dashboard KPIs and revenue chart",
    description=(
        "Returns KPI cards and daily revenue chart data.\n\n"
        "**KPIs returned:**\n"
        "- today / this_month / this_year: orders count & revenue\n"
        "- total_expenses_this_month\n"
        "- unpaid_credit_total\n\n"
        "**Chart:** last 30 days daily revenue"
    ),
)
class DashboardKPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {"GET": "orders.view_order"}

    def get(self, request):
        user = request.user
        today = date.today()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        chart_start = today - timedelta(days=29)

        # Base querysets scoped to user's org/branch
        orders_qs = _filter_by_org_branch(Order.objects.all(), user)
        expenses_qs = _filter_by_org_branch(Expense.objects.all(), user)

        def order_stats(qs):
            result = qs.aggregate(
                count=Count("id"),
                revenue=Coalesce(Sum("total"), Decimal("0.000"), output_field=DecimalField()),
            )
            return {"orders": result["count"], "revenue": result["revenue"]}

        # KPIs
        today_qs = orders_qs.filter(inward_date=today)
        month_qs = orders_qs.filter(inward_date__gte=month_start)
        year_qs = orders_qs.filter(inward_date__gte=year_start)

        expenses_this_month = expenses_qs.filter(
            expense_date__gte=month_start
        ).aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.000"), output_field=DecimalField())
        )["total"]

        # Unpaid credit = sum of credit payments - sum of repayments
        credit_total = OrderPayment.objects.filter(
            order__in=orders_qs, payment_type="credit"
        ).aggregate(
            total=Coalesce(Sum("received_amount"), Decimal("0.000"), output_field=DecimalField())
        )["total"]

        repaid_total = OrderPayment.objects.filter(
            order__in=orders_qs, payment_type="repayment"
        ).aggregate(
            total=Coalesce(Sum("received_amount"), Decimal("0.000"), output_field=DecimalField())
        )["total"]

        unpaid_credit = max(Decimal("0"), credit_total - repaid_total)

        # Revenue chart: last 30 days
        chart_data = (
            orders_qs.filter(inward_date__gte=chart_start)
            .annotate(day=TruncDate("inward_date"))
            .values("day")
            .annotate(revenue=Coalesce(Sum("total"), Decimal("0.000"), output_field=DecimalField()))
            .order_by("day")
        )

        # Fill missing days with 0
        revenue_map = {row["day"]: float(row["revenue"]) for row in chart_data}
        chart = []
        for i in range(30):
            d = chart_start + timedelta(days=i)
            chart.append({"date": str(d), "revenue": revenue_map.get(d, 0.0)})

        return Response({
            "kpis": {
                "today": order_stats(today_qs),
                "this_month": order_stats(month_qs),
                "this_year": order_stats(year_qs),
                "expenses_this_month": float(expenses_this_month),
                "unpaid_credit_total": float(unpaid_credit),
            },
            "revenue_chart": chart,
        })


# ----------------------------- P&L Report --------------------------------

@extend_schema(
    tags=["Reports: P&L"],
    summary="Profit & Loss Report",
    description="Returns revenue, expenses, and net profit for a date range.",
    parameters=[
        OpenApiParameter("from_date", OpenApiTypes.DATE, description="Start date (YYYY-MM-DD)"),
        OpenApiParameter("to_date", OpenApiTypes.DATE, description="End date (YYYY-MM-DD)"),
    ],
)
class PnLReportView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {"GET": "orders.view_order"}

    def get(self, request):
        user = request.user
        today = date.today()
        from_date = _parse_date(request.query_params.get("from_date"), today.replace(day=1))
        to_date = _parse_date(request.query_params.get("to_date"), today)

        orders_qs = _filter_by_org_branch(Order.objects.all(), user)
        expenses_qs = _filter_by_org_branch(Expense.objects.all(), user)

        # Revenue
        revenue_data = orders_qs.filter(
            inward_date__gte=from_date, inward_date__lte=to_date
        ).aggregate(
            total_orders=Count("id"),
            gross_revenue=Coalesce(Sum("total"), Decimal("0.000"), output_field=DecimalField()),
            total_vat=Coalesce(Sum("vat_price"), Decimal("0.000"), output_field=DecimalField()),
            total_discount=Coalesce(Sum("discount_price"), Decimal("0.000"), output_field=DecimalField()),
        )

        # Expenses
        expense_data = expenses_qs.filter(
            expense_date__gte=from_date, expense_date__lte=to_date
        ).aggregate(
            total_expenses=Coalesce(Sum("amount"), Decimal("0.000"), output_field=DecimalField()),
            expense_count=Count("id"),
        )

        # Expense breakdown by category
        category_breakdown = list(
            expenses_qs.filter(expense_date__gte=from_date, expense_date__lte=to_date)
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        gross_revenue = revenue_data["gross_revenue"] or Decimal("0")
        total_expenses = expense_data["total_expenses"] or Decimal("0")
        net_profit = gross_revenue - total_expenses

        return Response({
            "period": {"from": str(from_date), "to": str(to_date)},
            "revenue": {
                "total_orders": revenue_data["total_orders"],
                "gross_revenue": float(gross_revenue),
                "total_vat": float(revenue_data["total_vat"] or 0),
                "total_discount": float(revenue_data["total_discount"] or 0),
            },
            "expenses": {
                "total_expenses": float(total_expenses),
                "expense_count": expense_data["expense_count"],
                "by_category": [
                    {"category": r["category__name"] or "Uncategorized", "total": float(r["total"])}
                    for r in category_breakdown
                ],
            },
            "net_profit": float(net_profit),
            "profit_margin_percent": (
                round(float(net_profit / gross_revenue * 100), 2) if gross_revenue else 0.0
            ),
        })


# ----------------------------- Customer List Report --------------------------------

@extend_schema(
    tags=["Reports: Customers"],
    summary="Customer List Report",
    description="Full customer list with order totals, credit info, and last order date.",
    parameters=[
        OpenApiParameter("from_date", OpenApiTypes.DATE, description="Filter by order date from"),
        OpenApiParameter("to_date", OpenApiTypes.DATE, description="Filter by order date to"),
        OpenApiParameter("category", OpenApiTypes.INT, description="Filter by customer category ID"),
    ],
)
class CustomerListReportView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {"GET": "customers.view_customer"}

    def get(self, request):
        user = request.user
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        category_id = request.query_params.get("category")

        customers_qs = _filter_by_org_branch(Customer.objects.all(), user)
        if category_id:
            customers_qs = customers_qs.filter(category_id=category_id)

        # Build order filter
        order_filter = Q()
        if from_date:
            order_filter &= Q(orders__inward_date__gte=from_date)
        if to_date:
            order_filter &= Q(orders__inward_date__lte=to_date)

        customers_qs = customers_qs.annotate(
            total_orders=Count("orders", filter=order_filter),
            total_amount=Coalesce(
                Sum("orders__total", filter=order_filter),
                Decimal("0.000"),
                output_field=DecimalField(),
            ),
            total_credit=Coalesce(
                Sum(
                    "orders__payments__received_amount",
                    filter=Q(orders__payments__payment_type="credit"),
                ),
                Decimal("0.000"),
                output_field=DecimalField(),
            ),
            total_repaid=Coalesce(
                Sum(
                    "orders__payments__received_amount",
                    filter=Q(orders__payments__payment_type="repayment"),
                ),
                Decimal("0.000"),
                output_field=DecimalField(),
            ),
        ).select_related("category")

        data = []
        for c in customers_qs:
            unpaid = max(Decimal("0"), (c.total_credit or 0) - (c.total_repaid or 0))
            data.append({
                "id": c.id,
                "customer_id": c.customer_id,
                "name": c.name,
                "mobile": f"{c.country_code or ''}{c.mobile_number or ''}",
                "email": c.email,
                "category": c.category.name if c.category else None,
                "credit_limit": float(c.credit_limit or 0),
                "total_orders": c.total_orders,
                "total_amount": float(c.total_amount or 0),
                "credit_used": float(c.total_credit or 0),
                "credit_repaid": float(c.total_repaid or 0),
                "unpaid_balance": float(unpaid),
                "is_active": c.is_active,
            })

        return Response({"count": len(data), "results": data})


# ----------------------------- Unpaid Customers Report --------------------------------

@extend_schema(
    tags=["Reports: Customers"],
    summary="Unpaid Customers Report",
    description="Lists customers with outstanding (unpaid) credit balance > 0.",
)
class UnpaidCustomersReportView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    permission_map = {"GET": "customers.view_customer"}

    def get(self, request):
        user = request.user
        customers_qs = _filter_by_org_branch(Customer.objects.all(), user)

        customers_qs = customers_qs.annotate(
            total_credit=Coalesce(
                Sum(
                    "orders__payments__received_amount",
                    filter=Q(orders__payments__payment_type="credit"),
                ),
                Decimal("0.000"),
                output_field=DecimalField(),
            ),
            total_repaid=Coalesce(
                Sum(
                    "orders__payments__received_amount",
                    filter=Q(orders__payments__payment_type="repayment"),
                ),
                Decimal("0.000"),
                output_field=DecimalField(),
            ),
        ).annotate(
            unpaid_balance=ExpressionWrapper(
                F("total_credit") - F("total_repaid"),
                output_field=DecimalField(max_digits=12, decimal_places=3),
            )
        ).filter(unpaid_balance__gt=0).select_related("category").order_by("-unpaid_balance")

        data = []
        for c in customers_qs:
            data.append({
                "id": c.id,
                "customer_id": c.customer_id,
                "name": c.name,
                "mobile": f"{c.country_code or ''}{c.mobile_number or ''}",
                "email": c.email,
                "category": c.category.name if c.category else None,
                "credit_limit": float(c.credit_limit or 0),
                "credit_used": float(c.total_credit or 0),
                "credit_repaid": float(c.total_repaid or 0),
                "unpaid_balance": float(c.unpaid_balance),
            })

        total_unpaid = sum(r["unpaid_balance"] for r in data)
        return Response({
            "count": len(data),
            "total_unpaid": round(total_unpaid, 3),
            "results": data,
        })
