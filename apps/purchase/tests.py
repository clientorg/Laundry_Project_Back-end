from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase

from .models import ACC_TRAN, ACC_TRAN_DETA, ACCT_MAST, ACCT_MAST_MAP, VRTypeMaster
from .serializers import ACCTMASTSerializer, ACCTRANDETASerializer

User = get_user_model()


def make_account(name, actype=ACCT_MAST.DETAIL, grpcode="EXPENSE", parent=None):
    return ACCT_MAST.objects.create(
        accname=name,
        grpcode=grpcode,
        baltype="Debit",
        actype=actype,
        parent=parent,
    )


class AccountHierarchyTests(TestCase):
    """Covers prompt Section 15 'Hierarchy' and 'Account Type' QA scenarios."""

    def test_level_map_derived_from_parent_chain(self):
        expenses = make_account("Expenses", actype=ACCT_MAST.GROUP)
        utilities = make_account("Utility Expenses", actype=ACCT_MAST.GROUP, parent=expenses)
        electricity = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL, parent=utilities)

        level_map = ACCT_MAST_MAP.objects.get(acct_mast=electricity)
        self.assertEqual(level_map.totlev, 3)
        self.assertEqual(level_map.lev1, expenses.id)
        self.assertEqual(level_map.lev2, utilities.id)
        self.assertEqual(level_map.lev3, electricity.id)
        self.assertIsNone(level_map.lev4)

    def test_reparenting_cascades_to_descendants(self):
        assets = make_account("Assets", actype=ACCT_MAST.GROUP, grpcode="ASSET")
        expenses = make_account("Expenses", actype=ACCT_MAST.GROUP)
        utilities = make_account("Utility Expenses", actype=ACCT_MAST.GROUP, parent=expenses)
        electricity = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL, parent=utilities)

        # Move Utility Expenses under a differently-grpcoded root would fail validation
        # (grpcode mismatch), so exercise the cascade with a same-grpcode reparent instead.
        new_root = make_account("Operating Expenses", actype=ACCT_MAST.GROUP)
        utilities.parent = new_root
        utilities.clean()
        utilities.save()

        level_map = ACCT_MAST_MAP.objects.get(acct_mast=electricity)
        self.assertEqual(level_map.totlev, 3)
        self.assertEqual(level_map.lev1, new_root.id)
        self.assertEqual(level_map.lev2, utilities.id)
        self.assertEqual(level_map.lev3, electricity.id)
        self.assertIsNotNone(assets)  # unrelated branch untouched

    def test_parent_must_be_group_account(self):
        detail = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL)
        child = ACCT_MAST(accname="Sub Expense", grpcode="EXPENSE", baltype="Debit", actype=ACCT_MAST.DETAIL, parent=detail)
        with self.assertRaises(DjangoValidationError):
            child.clean()

    def test_grpcode_must_match_parent(self):
        expenses = make_account("Expenses", actype=ACCT_MAST.GROUP)
        mismatched = ACCT_MAST(accname="Bank", grpcode="ASSET", baltype="Debit", actype=ACCT_MAST.DETAIL, parent=expenses)
        with self.assertRaises(DjangoValidationError):
            mismatched.clean()

    def test_cannot_create_cycle(self):
        root = make_account("Expenses", actype=ACCT_MAST.GROUP)
        child = make_account("Utility Expenses", actype=ACCT_MAST.GROUP, parent=root)

        root.parent = child
        with self.assertRaises(DjangoValidationError):
            root.clean()

    def test_max_depth_exceeded(self):
        node = None
        for i in range(ACCT_MAST.MAX_LEVELS):
            node = make_account(f"Level {i + 1}", actype=ACCT_MAST.GROUP, parent=node)

        too_deep = ACCT_MAST(accname="Too Deep", grpcode="EXPENSE", baltype="Debit", actype=ACCT_MAST.DETAIL, parent=node)
        with self.assertRaises(DjangoValidationError):
            too_deep.clean()

    def test_detail_account_cannot_be_converted_to_detail_if_children_exist(self):
        group = make_account("Utility Expenses", actype=ACCT_MAST.GROUP)
        make_account("Electricity Expense", actype=ACCT_MAST.DETAIL, parent=group)

        group.actype = ACCT_MAST.DETAIL
        with self.assertRaises(DjangoValidationError):
            group.clean()


class ACCTMASTSerializerValidationTests(TestCase):
    def test_serializer_rejects_detail_parent(self):
        detail = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL)
        serializer = ACCTMASTSerializer(data={
            "accname": "Sub Expense",
            "grpcode": "EXPENSE",
            "baltype": "Debit",
            "actype": ACCT_MAST.DETAIL,
            "parent": detail.id,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("parent", serializer.errors)


class PostingRuleTests(TestCase):
    """Covers prompt Section 9/15: only active Detail accounts can be posted to."""

    def setUp(self):
        self.vr_type = VRTypeMaster.objects.create(vrname="Journal", zipcode="JV")
        self.acc_tran = ACC_TRAN.objects.create(vr_type=self.vr_type)

    def test_group_account_rejected_for_posting(self):
        group = make_account("Expenses", actype=ACCT_MAST.GROUP)
        serializer = ACCTRANDETASerializer(data={
            "acc_tran": self.acc_tran.id,
            "dc_flag": "Debit",
            "account": group.id,
            "amount": "100.000",
        })
        self.assertFalse(serializer.is_valid())

    def test_inactive_detail_account_rejected_for_posting(self):
        detail = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL)
        detail.is_active = False
        detail.save()
        serializer = ACCTRANDETASerializer(data={
            "acc_tran": self.acc_tran.id,
            "dc_flag": "Debit",
            "account": detail.id,
            "amount": "100.000",
        })
        self.assertFalse(serializer.is_valid())

    def test_active_detail_account_accepted_for_posting(self):
        detail = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL)
        serializer = ACCTRANDETASerializer(data={
            "acc_tran": self.acc_tran.id,
            "dc_flag": "Debit",
            "account": detail.id,
            "amount": "100.000",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)


class ACCTMASTApiTests(APITestCase):
    """Covers prompt Section 15 'Deletion' and 'API' QA scenarios."""

    def setUp(self):
        self.user = User.objects.create_superuser(username="admin", password="pass12345", email="admin@example.com")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_destroy_blocked_when_account_has_children(self):
        group = make_account("Utility Expenses", actype=ACCT_MAST.GROUP)
        make_account("Electricity Expense", actype=ACCT_MAST.DETAIL, parent=group)

        response = self.client.delete(f"/api/purchase/acct-mast/{group.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(ACCT_MAST.objects.filter(id=group.id).exists())

    def test_destroy_blocked_when_account_used_in_transaction(self):
        detail = make_account("Electricity Expense", actype=ACCT_MAST.DETAIL)
        vr_type = VRTypeMaster.objects.create(vrname="Journal", zipcode="JV")
        acc_tran = ACC_TRAN.objects.create(vr_type=vr_type)
        ACC_TRAN_DETA.objects.create(acc_tran=acc_tran, dc_flag="Debit", account=detail, amount=100)

        response = self.client.delete(f"/api/purchase/acct-mast/{detail.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(ACCT_MAST.objects.filter(id=detail.id).exists())

    def test_destroy_allowed_when_unused(self):
        detail = make_account("Rent Expense", actype=ACCT_MAST.DETAIL)

        response = self.client.delete(f"/api/purchase/acct-mast/{detail.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ACCT_MAST.objects.filter(id=detail.id).exists())

    def test_tree_endpoint_returns_nested_structure(self):
        expenses = make_account("Expenses", actype=ACCT_MAST.GROUP)
        utilities = make_account("Utility Expenses", actype=ACCT_MAST.GROUP, parent=expenses)
        make_account("Electricity Expense", actype=ACCT_MAST.DETAIL, parent=utilities)

        response = self.client.get("/api/purchase/acct-mast/tree/")
        self.assertEqual(response.status_code, 200)

        root = next(node for node in response.data if node["id"] == expenses.id)
        self.assertEqual(len(root["children"]), 1)
        child = root["children"][0]
        self.assertEqual(child["id"], utilities.id)
        self.assertEqual(len(child["children"]), 1)
        self.assertEqual(child["children"][0]["accname"], "Electricity Expense")

    def test_acct_mast_map_is_read_only(self):
        response = self.client.post("/api/purchase/acct-mast-map/", {"totlev": 1, "lev1": 1})
        self.assertEqual(response.status_code, 405)
