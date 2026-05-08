"""
Smoke test for PurchaseInvoice creation.

Usage:
    python manage.py test_purchase_invoice
"""
import datetime

from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model

from apps.purchase.models import (
    SupplierMaster, VATMaster, VRTypeMaster,
    ItemMaster, UnitMaster, PurchaseInvoice,
)
from apps.purchase.serializers import PurchaseInvoiceSerializer

User = get_user_model()


class Command(BaseCommand):
    help = "Smoke test: create a PurchaseInvoice via the serializer and verify it saves correctly."

    def handle(self, *args, **options):
        self.stdout.write("\n=== Purchase Invoice creation smoke test ===\n")

        # ── 1. grab a usable user ──────────────────────────────────────────────
        user = User.objects.filter(is_active=True).first()
        if not user:
            self.stderr.write(self.style.ERROR("No active user found – seed the DB first."))
            return
        self._ok(f"Using user: {user.username}")

        # ── 2. fake request ───────────────────────────────────────────────────
        factory = RequestFactory()
        request = factory.post("/api/purchase/purchase-invoice/")
        request.user = user

        # ── 3. build payload ──────────────────────────────────────────────────
        payload = {
            "invoice_date": str(datetime.date.today()),
            "paymode": "cash",
            "status": "draft",
            "amount_ex_vat": "100.000",
            "lines": [],
        }

        supplier = SupplierMaster.objects.first()
        if supplier:
            payload["supplier"] = supplier.id
            self._ok(f"Using supplier: {supplier.name} (id={supplier.id})")
        else:
            self._warn("No supplier found – skipping supplier field")

        vat = VATMaster.objects.first()
        if vat:
            payload["vat"] = vat.id
            self._ok(f"Using VAT: {vat.vatname} ({vat.vatper}%)")
        else:
            self._warn("No VAT found – skipping vat field")

        vr_type = VRTypeMaster.objects.first()
        if vr_type:
            payload["vr_type"] = vr_type.id
            self._ok(f"Using VR Type: {vr_type.vrname} (id={vr_type.id})")
        else:
            self._warn("No VR Type found – skipping vr_type field")

        # ── 4. test without lines ─────────────────────────────────────────────
        self.stdout.write("\n-- Test 1: invoice without lines --")
        self._run_test(payload, request, user, with_lines=False)

        # ── 5. test with lines ────────────────────────────────────────────────
        item = ItemMaster.objects.first()
        unit = UnitMaster.objects.first()
        if item and unit:
            payload_with_lines = dict(payload)
            payload_with_lines["lines"] = [
                {"item": item.id, "unit": unit.id, "qty": "2.000", "rate": "50.000"},
            ]
            self.stdout.write("\n-- Test 2: invoice with 1 line item --")
            self._ok(f"Using item: {item.itname} (id={item.id}), unit: {unit.unitname} (id={unit.id})")
            self._run_test(payload_with_lines, request, user, with_lines=True)
        else:
            self._warn("No item/unit found – skipping lines test")

        self.stdout.write(self.style.SUCCESS("\n=== ALL TESTS PASSED ===\n"))

    # ── helpers ────────────────────────────────────────────────────────────────

    def _run_test(self, payload, request, user, with_lines):
        serializer = PurchaseInvoiceSerializer(
            data=payload, context={"request": request}
        )

        if not serializer.is_valid():
            self.stderr.write(self.style.ERROR(f"Validation errors: {serializer.errors}"))
            raise SystemExit(1)
        self._ok("Serializer is valid")

        try:
            invoice = serializer.save()
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"serializer.save() raised {type(e).__name__}: {e}"
            ))
            raise SystemExit(1)

        self._ok(f"Invoice created: {invoice.invoice_no}  (id={invoice.id})")
        self._ok(f"  amount_ex_vat  = {invoice.amount_ex_vat}")
        self._ok(f"  vat_amount     = {invoice.vat_amount}")
        self._ok(f"  amount_inc_vat = {invoice.amount_inc_vat}")
        self._ok(f"  branches count = {invoice.branches.count()}")
        self._ok(f"  organization   = {invoice.organization}")

        if with_lines:
            line_count = invoice.lines.count()
            self._ok(f"  lines saved    = {line_count}")
            if line_count == 0:
                self.stderr.write(self.style.ERROR("Expected at least 1 line but got 0!"))
                raise SystemExit(1)

        # verify in DB
        from_db = PurchaseInvoice.objects.filter(id=invoice.id).first()
        if not from_db:
            self.stderr.write(self.style.ERROR("Invoice not found in DB after save!"))
            raise SystemExit(1)
        self._ok(f"Verified in DB: {from_db.invoice_no}")

        # clean up
        from_db.delete()
        self._ok("Test invoice deleted (clean up done)")

    def _ok(self, msg):
        self.stdout.write(self.style.SUCCESS(f"  ✓  {msg}"))

    def _warn(self, msg):
        self.stdout.write(self.style.WARNING(f"  ⚠  {msg}"))
