from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import FieldDoesNotExist
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
from apps.purchase.models import PurchaseInvoice


def _parse_date(value, fallback):
    if not value:
        return fallback
    try:
        from datetime import datetime
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return fallback


def _filter_by_org_branch(qs, user, org_field="organization", branch_field="branches"):
    """
    Mirrors OrgBranchQuerysetMixin logic for APIView querysets.

    - Org user  → records belonging to that org OR any of its branches.
    - Branch user → records assigned to those branches; also includes
      is_global records scoped to the parent org (when the model has that field).
    - Neither   → empty queryset.
    """
    if user.organization:
        return qs.filter(
            Q(**{org_field: user.organization})
            | Q(**{f"{branch_field}__parent": user.organization})
        ).distinct()

    elif user.branches.exists():
        filters = Q(**{f"{branch_field}__in": user.branches.all()})

        # Include is_global items scoped to the parent org when supported.
        try:
            qs.model._meta.get_field("is_global")
            first_branch = user.branches.first()
            parent_org = first_branch.parent if first_branch else None
            if parent_org:
                filters |= Q(is_global=True) & (
                    Q(**{org_field: parent_org})
                    | Q(**{f"{branch_field}__parent": parent_org})
                )
        except FieldDoesNotExist:
            pass

        return qs.filter(filters).distinct()

    return qs.none()


# ----------------------------- Dashboard KPIs --------------------------------

@extend_schema(
    tags=["Reports: Dashboard"],
    summary="Dashboard KPIs and revenue chart",
    description=(
        "Returns KPI cards and order/revenue chart data.\n\n"
        "**KPIs returned:**\n"
        "- `today` / `this_month` / `this_year`: orders count, revenue, collected_amount, credit_given\n"
        "- `expenses_this_month`\n"
        "- `unpaid_credit_total` — all-time outstanding credit (see `unpaid_credit_label` for period)\n\n"
        "**Chart:** daily (≤60 days) or weekly (>60 days) order counts + revenue.\n"
        "Use `chart_period` for a preset range or `chart_from`/`chart_to` for a custom range. "
        "Defaults to last 30 days."
    ),
    parameters=[
        OpenApiParameter("chart_period", OpenApiTypes.INT, description="Preset range in days: 7, 14, 30 (default), 60, or 90"),
        OpenApiParameter("chart_from", OpenApiTypes.DATE, description="Custom chart start date (YYYY-MM-DD)"),
        OpenApiParameter("chart_to", OpenApiTypes.DATE, description="Custom chart end date (YYYY-MM-DD)"),
    ],
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

        D0 = Decimal("0.000")

        # Base querysets scoped to user's org/branch
        orders_qs = _filter_by_org_branch(Order.objects.all(), user)
        expenses_qs = _filter_by_org_branch(Expense.objects.all(), user)

        def _order_stats(qs):
            """Revenue + collected + credit_given for a set of orders."""
            revenue = qs.aggregate(
                count=Count("id"),
                revenue=Coalesce(Sum("total"), D0, output_field=DecimalField()),
            )
            payments = OrderPayment.objects.filter(order__in=qs)
            collected = float(
                payments.exclude(payment_type__in=["credit"]).aggregate(
                    t=Coalesce(Sum("received_amount"), D0, output_field=DecimalField())
                )["t"]
            )
            credit_given = float(
                payments.filter(payment_type="credit").aggregate(
                    t=Coalesce(Sum("received_amount"), D0, output_field=DecimalField())
                )["t"]
            )
            return {
                "orders": revenue["count"],
                "revenue": float(revenue["revenue"]),
                "collected_amount": collected,
                "credit_given": credit_given,
            }

        # ── KPI periods ────────────────────────────────────────────────
        today_qs = orders_qs.filter(inward_date=today)
        month_qs = orders_qs.filter(inward_date__gte=month_start)
        year_qs = orders_qs.filter(inward_date__gte=year_start)

        expenses_this_month = expenses_qs.filter(
            expense_date__gte=month_start
        ).aggregate(
            total=Coalesce(Sum("amount"), D0, output_field=DecimalField())
        )["total"]

        # All-time unpaid credit scoped to the user's org/branch
        all_payments = OrderPayment.objects.filter(order__in=orders_qs)
        credit_total = float(
            all_payments.filter(payment_type="credit").aggregate(
                t=Coalesce(Sum("received_amount"), D0, output_field=DecimalField())
            )["t"]
        )
        repaid_total = float(
            all_payments.filter(payment_type="repayment").aggregate(
                t=Coalesce(Sum("received_amount"), D0, output_field=DecimalField())
            )["t"]
        )
        unpaid_credit = max(0.0, credit_total - repaid_total)

        # ── Revenue chart — dynamic period / grouping ──────────────────
        chart_period_param = request.query_params.get("chart_period")
        chart_from_param = request.query_params.get("chart_from")
        chart_to_param = request.query_params.get("chart_to")

        if chart_from_param and chart_to_param:
            chart_end = _parse_date(chart_to_param, today)
            chart_start = _parse_date(chart_from_param, today - timedelta(days=29))
        else:
            try:
                period_days = int(chart_period_param) if chart_period_param else 30
                if period_days not in (7, 14, 30, 60, 90):
                    period_days = 30
            except (ValueError, TypeError):
                period_days = 30
            chart_end = today
            chart_start = today - timedelta(days=period_days - 1)

        days_span = (chart_end - chart_start).days + 1
        grouping = "daily" if days_span <= 60 else "weekly"

        chart_orders = orders_qs.filter(inward_date__gte=chart_start, inward_date__lte=chart_end)

        revenue_rows = list(
            chart_orders
            .values("inward_date")
            .annotate(
                orders=Count("id"),
                revenue=Coalesce(Sum("total"), D0, output_field=DecimalField()),
            )
            .order_by("inward_date")
        )
        collected_rows = list(
            OrderPayment.objects
            .filter(order__in=chart_orders)
            .exclude(payment_type="credit")
            .values("order__inward_date")
            .annotate(collected=Coalesce(Sum("received_amount"), D0, output_field=DecimalField()))
        )

        if grouping == "daily":
            revenue_map = {row["inward_date"]: float(row["revenue"]) for row in revenue_rows}
            orders_map = {row["inward_date"]: row["orders"] for row in revenue_rows}
            collected_map = {row["order__inward_date"]: float(row["collected"]) for row in collected_rows}

            chart = []
            for i in range(days_span):
                d = chart_start + timedelta(days=i)
                chart.append({
                    "date": str(d),
                    "orders": orders_map.get(d, 0),
                    "revenue": revenue_map.get(d, 0.0),
                    "collected": collected_map.get(d, 0.0),
                })
        else:
            def _week_monday(d):
                return d - timedelta(days=d.weekday())

            weekly_orders = {}
            weekly_revenue = {}
            for row in revenue_rows:
                wk = _week_monday(row["inward_date"])
                weekly_orders[wk] = weekly_orders.get(wk, 0) + row["orders"]
                weekly_revenue[wk] = weekly_revenue.get(wk, 0.0) + float(row["revenue"])

            weekly_collected = {}
            for row in collected_rows:
                wk = _week_monday(row["order__inward_date"])
                weekly_collected[wk] = weekly_collected.get(wk, 0.0) + float(row["collected"])

            chart = []
            wk = _week_monday(chart_start)
            while wk <= chart_end:
                chart.append({
                    "date": str(wk),
                    "week_end": str(min(wk + timedelta(days=6), chart_end)),
                    "orders": weekly_orders.get(wk, 0),
                    "revenue": weekly_revenue.get(wk, 0.0),
                    "collected": weekly_collected.get(wk, 0.0),
                })
                wk += timedelta(weeks=1)

        return Response({
            "kpis": {
                "today": _order_stats(today_qs),
                "this_month": _order_stats(month_qs),
                "this_year": _order_stats(year_qs),
                "expenses_this_month": float(expenses_this_month),
                "unpaid_credit_total": round(unpaid_credit, 3),
                "unpaid_credit_period": "all_time",
                "unpaid_credit_label": "Total Outstanding (All Time)",
            },
            "revenue_chart": {
                "grouping": grouping,
                "from": str(chart_start),
                "to": str(chart_end),
                "data": chart,
            },
        })


# ----------------------------- P&L Report --------------------------------

@extend_schema(
    tags=["Reports: P&L"],
    summary="Profit & Loss Report",
    description=(
        "Detailed P&L for a date range.\n\n"
        "**Sections returned:**\n"
        "- `order_revenue` — gross revenue, base price, VAT collected, discounts, delivery charges\n"
        "- `payment_collections` — breakdown by payment type (cash/card/upi/wallet/credit/repaid)\n"
        "- `purchase_cost` — purchase invoices (ex-VAT, VAT, inc-VAT)\n"
        "- `direct_expenses` — total expenses with per-category breakdown\n"
        "- `summary` — total_income, purchase_cost, gross_profit, direct_expenses, net_profit, profit_margin_%"
    ),
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

        D0 = Decimal("0.000")

        orders_qs = _filter_by_org_branch(Order.objects.all(), user)
        expenses_qs = _filter_by_org_branch(Expense.objects.all(), user)
        purchase_qs = _filter_by_org_branch(PurchaseInvoice.objects.filter(is_active=True), user)

        period_orders = orders_qs.filter(inward_date__gte=from_date, inward_date__lte=to_date)
        period_expenses = expenses_qs.filter(expense_date__gte=from_date, expense_date__lte=to_date)
        period_purchases = purchase_qs.filter(invoice_date__gte=from_date, invoice_date__lte=to_date)

        # ── Order Revenue ──────────────────────────────────────────────
        revenue_data = period_orders.aggregate(
            total_orders=Count("id"),
            gross_revenue=Coalesce(Sum("total"), D0, output_field=DecimalField()),
            order_price=Coalesce(Sum("price"), D0, output_field=DecimalField()),
            vat_collected=Coalesce(Sum("vat_price"), D0, output_field=DecimalField()),
            discount_given=Coalesce(Sum("discount_price"), D0, output_field=DecimalField()),
            delivery_charges=Coalesce(Sum("delivery_charge_price"), D0, output_field=DecimalField()),
        )

        # ── Payment Collections ────────────────────────────────────────
        payments_qs = OrderPayment.objects.filter(order__in=period_orders)

        def _pay_sum(ptype):
            return float(
                payments_qs.filter(payment_type=ptype).aggregate(
                    t=Coalesce(Sum("received_amount"), D0, output_field=DecimalField())
                )["t"]
            )

        payment_collections = {
            "cash": _pay_sum("cash"),
            "card": _pay_sum("card"),
            "upi": _pay_sum("upi"),
            "wallet": _pay_sum("wallet"),
            "credit_given": _pay_sum("credit"),
            "credit_repaid": _pay_sum("repayment"),
            "other": _pay_sum("other"),
        }
        payment_collections["net_credit_outstanding"] = round(
            payment_collections["credit_given"] - payment_collections["credit_repaid"], 3
        )

        # ── Purchase Cost ──────────────────────────────────────────────
        purchase_data = period_purchases.aggregate(
            invoice_count=Count("id"),
            purchase_ex_vat=Coalesce(Sum("amount_ex_vat"), D0, output_field=DecimalField()),
            purchase_vat=Coalesce(Sum("vat_amount"), D0, output_field=DecimalField()),
            purchase_total=Coalesce(Sum("amount_inc_vat"), D0, output_field=DecimalField()),
        )

        # ── Direct Expenses ────────────────────────────────────────────
        expense_data = period_expenses.aggregate(
            expense_count=Count("id"),
            total_expenses=Coalesce(Sum("amount"), D0, output_field=DecimalField()),
        )
        expense_by_category = list(
            period_expenses
            .values("category__name")
            .annotate(total=Coalesce(Sum("amount"), D0, output_field=DecimalField()))
            .order_by("-total")
        )

        # ── Summary ────────────────────────────────────────────────────
        total_income = revenue_data["gross_revenue"] or D0
        purchase_cost = purchase_data["purchase_total"] or D0
        direct_expenses = expense_data["total_expenses"] or D0
        gross_profit = total_income - purchase_cost
        net_profit = gross_profit - direct_expenses

        return Response({
            "period": {"from": str(from_date), "to": str(to_date)},

            "order_revenue": {
                "total_orders": revenue_data["total_orders"],
                "gross_revenue": float(revenue_data["gross_revenue"]),
                "order_price": float(revenue_data["order_price"]),
                "vat_collected": float(revenue_data["vat_collected"]),
                "discount_given": float(revenue_data["discount_given"]),
                "delivery_charges": float(revenue_data["delivery_charges"]),
            },

            "payment_collections": payment_collections,

            "purchase_cost": {
                "invoice_count": purchase_data["invoice_count"],
                "amount_ex_vat": float(purchase_data["purchase_ex_vat"]),
                "vat_amount": float(purchase_data["purchase_vat"]),
                "amount_inc_vat": float(purchase_data["purchase_total"]),
            },

            "direct_expenses": {
                "expense_count": expense_data["expense_count"],
                "total_expenses": float(direct_expenses),
                "by_category": [
                    {
                        "category": r["category__name"] or "Uncategorized",
                        "total": float(r["total"]),
                    }
                    for r in expense_by_category
                ],
            },

            "summary": {
                "total_income": float(total_income),
                "purchase_cost": float(purchase_cost),
                "gross_profit": float(gross_profit),
                "direct_expenses": float(direct_expenses),
                "total_cost": float(purchase_cost + direct_expenses),
                "net_profit": float(net_profit),
                "profit_margin_percent": (
                    round(float(net_profit / total_income * 100), 2) if total_income else 0.0
                ),
            },
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
                "category": {"id": c.category.id, "name": c.category.name} if c.category else None,
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
                "category": {"id": c.category.id, "name": c.category.name} if c.category else None,
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
