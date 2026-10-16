from django.test import TestCase

from apps.purchase.models import ACCT_MAST
from .serializers import ExpenseSerializer


def make_account(name, actype=ACCT_MAST.DETAIL, grpcode="EXPENSE"):
    return ACCT_MAST.objects.create(
        accname=name,
        grpcode=grpcode,
        baltype="Debit",
        actype=actype,
    )


class ExpenseGLAccountValidationTests(TestCase):
    """Covers prompt Section 10/15: Expense must post only to active Detail/Posting accounts."""

    def test_group_account_rejected_as_gl_account(self):
        group = make_account("Utility Expenses", actype=ACCT_MAST.GROUP)
        serializer = ExpenseSerializer(data={
            "expense_date": "2026-08-21",
            "gl_account": group.id,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_inactive_detail_account_rejected_as_gl_account(self):
        detail = make_account("Electricity Expense")
        detail.is_active = False
        detail.save()
        serializer = ExpenseSerializer(data={
            "expense_date": "2026-08-21",
            "gl_account": detail.id,
        })
        self.assertFalse(serializer.is_valid())

    def test_active_detail_account_accepted_as_gl_account(self):
        detail = make_account("Electricity Expense")
        serializer = ExpenseSerializer(data={
            "expense_date": "2026-08-21",
            "gl_account": detail.id,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
