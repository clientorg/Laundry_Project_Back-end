# Chart of Accounts: Account Master & Account Map Master

This documents the relationship between `ACCT_MAST` (Account Master / GL accounts)
and `ACCT_MAST_MAP` (Account Map Master), what changed, and how to use the APIs.

## 1. Relationship diagram (current)

```text
ACCT_MAST (Account Master / GL accounts)
    id
    parent ───────────┐  self-FK, nullable. Only accounts with
    accname            │  actype = "General / Group" may be a parent.
    grpcode             │
    actype (Group|Detail)
    is_active
    ...
        │
        │ 1-to-1, auto-maintained on every ACCT_MAST.save()
        ▼
ACCT_MAST_MAP (derived breadcrumb, read-only via API)
    acct_mast ─────────► FK to the ACCT_MAST row this breadcrumb describes
    totlev              number of ancestor levels, including self
    lev1 .. lev8        ACCT_MAST.id of each ancestor, root-first,
                         self at position `totlev`
```

Before this change, `ACCT_MAST.acmapno` and `ACCT_MAST_MAP.acmapno` were each
auto-incremented independently in their own `save()` — they were never actually
a shared key, just two counters that happened to look similar. `lev1..lev8` were
plain integers with no FK to anything. There was no `parent` field on `ACCT_MAST`
at all, so the two tables were, in practice, unrelated. `ACCT_MAST_MAP.acct_mast`
is the new, real join key.

## 2. What Account Map Master (`ACCT_MAST_MAP`) is

It is **not** an independently editable list. It's a derived cache: for a given
account, `lev1..levN` list the `id`s of its ancestors from the root group down to
itself (`totlev` = N). It's recomputed automatically by `ACCT_MAST.save()`
(`_cascade_level_map`) whenever an account's `parent` changes — the whole subtree
is recomputed, since reparenting one Group shifts the breadcrumb of every
descendant. The `/api/purchase/acct-mast-map/` endpoint is now **read-only**
(`GET` list/retrieve only; `POST`/`PUT`/`PATCH`/`DELETE` return `405`). To
change the hierarchy, set `parent` on the account via `/api/purchase/acct-mast/`.

## 3. What Account Master (`ACCT_MAST`) is

The actual GL accounts, now including hierarchy via `parent`:

| Field | Meaning |
|---|---|
| `acno` | Auto-generated account number |
| `accname` / `accname_ar` | Account name (English / Arabic) |
| `grpcode` | Top-level classification: ASSET / LIABILITY / INCOME / EXPENSE |
| `actype` | `"General / Group"` (non-posting, organizational) or `"Detail"` (posting) |
| `parent` | Parent account. Must be a `"General / Group"` account. |
| `baltype` | Debit / Credit |
| `opening_balance` / `curbal` | Balances |
| `is_active` | Deactivated accounts can't be selected for new postings |

## 4. Example: `lev1..lev8` meaning

```text
Expenses (id=2, Group)
  └── Utility Expenses (id=15, Group, parent=2)
        └── Electricity Expense (id=27, Detail, parent=15)
```

`ACCT_MAST_MAP` row for Electricity Expense (`acct_mast=27`):

```json
{"acct_mast": 27, "totlev": 3, "lev1": 2, "lev2": 15, "lev3": 27, "lev4": null, ...}
```

`lev1=2 → Expenses`, `lev2=15 → Utility Expenses`, `lev3=27 → Electricity Expense`
(itself). Maximum depth is 8 levels (`ACCT_MAST.MAX_LEVELS`), matching `lev1..lev8`.

## 5. API examples

**Create a Group account:**
```http
POST /api/purchase/acct-mast/
{"accname": "Expenses", "grpcode": "EXPENSE", "baltype": "Debit", "actype": "General / Group"}
```

**Create a Detail account under it:**
```http
POST /api/purchase/acct-mast/
{"accname": "Electricity Expense", "grpcode": "EXPENSE", "baltype": "Debit", "actype": "Detail", "parent": 15}
```

Response includes the derived breadcrumb:
```json
{"id": 27, "accname": "Electricity Expense", "parent": 15, "parent_name": "Utility Expenses",
 "hierarchy_path": [{"id": 2, "acno": 200000, "accname": "Expenses"},
                     {"id": 15, "acno": 200001, "accname": "Utility Expenses"},
                     {"id": 27, "acno": 200002, "accname": "Electricity Expense"}], ...}
```

**Chart of Accounts tree:**
```http
GET /api/purchase/acct-mast/tree/
GET /api/purchase/acct-mast/?search=electric
```
Returns a nested tree (`children` arrays), scoped to the caller's organization/branches
the same way `list` already is.

**Account Map (read-only, derived):**
```http
GET /api/purchase/acct-mast-map/
POST /api/purchase/acct-mast-map/   → 405, edit `parent` on the account instead
```

## 6. Parent/child & posting validation rules

Enforced in `ACCT_MAST.clean()` (called from `ACCTMASTSerializer.validate()`):

- `parent` must be a `"General / Group"` account (a Detail account can't have children).
- No cycles (an account can't be its own ancestor).
- Max depth: 8 levels.
- A child's `grpcode` must match its parent's `grpcode`.
- An account can't be switched to `actype="Detail"` while it still has children.

Enforced in the `ACCTMASTViewSet.destroy()` (mirrors the existing `ItemMaster`
delete-guard pattern in `apps/master/views.py`):
- Blocked if the account has children.
- Blocked if the account is referenced by `ACC_TRAN_DETA` or `Expense.gl_account`
  — deactivate (`is_active=False`) instead of deleting. Historical transactions
  are unaffected either way (`SET_NULL` on delete, but delete is blocked in these cases).

Enforced in `ACCTRANDETASerializer.validate()` and `ExpenseSerializer.validate()`:
- Only `actype="Detail"` **and** `is_active=True` accounts can be posted to.

## 7. Expense → GL account relationship

`Expense.gl_account` (new, additive FK to `ACCT_MAST`; the existing `Expense.category`
→ `ExpenseCategory` is unchanged and still available). `ExpenseSerializer.validate()`
rejects Group accounts and inactive accounts, mirroring the transaction-posting rule
above.

## 8. Changes made

- `apps/purchase/models.py`: added `ACCT_MAST.parent`, `ACCT_MAST_MAP.acct_mast`,
  hierarchy helpers/validation (`get_ancestors`, `is_ancestor_of`, `clean`) and
  auto-derivation (`_sync_level_map`, `_cascade_level_map`) on `ACCT_MAST`. Removed
  a dead/broken code path in `ACC_TRAN_DETA.save()` that referenced a non-existent
  `ACCT_MAST.listcode` field.
- `apps/purchase/serializers.py`: `ACCTMASTSerializer` gained `parent`,
  `parent_name`, `hierarchy_path`, and hierarchy validation. `ACCTMASTMAPSerializer`
  is now fully read-only. `ACCTRANDETASerializer` now validates Detail+active on
  `account` (previously validated a nonexistent `acno` field — dead code).
- `apps/purchase/views.py`: `ACCTMASTViewSet` gained `?search=`, `/tree/`, and a
  delete guard. `ACCT_MAST_MAPViewSet` became a `ReadOnlyModelViewSet`.
- `apps/expenses/models.py` / `serializers.py`: added `Expense.gl_account` (additive).
- `apps/purchase/admin.py`: exposed `parent` on the `ACCT_MAST` admin; made the
  `ACCT_MAST_MAP` admin fully read-only.

## 9. Database migrations

- `apps/purchase/migrations/0020_acct_mast_parent_acct_mast_map_acct_mast.py` — adds
  `ACCT_MAST.parent` and `ACCT_MAST_MAP.acct_mast`.
- `apps/purchase/migrations/0021_backfill_acct_mast_map.py` — data migration: every
  pre-existing `ACCT_MAST` row gets a derived map row with `totlev=1, lev1=<own id>`
  (accurate, since all existing accounts start with `parent=NULL` — old `lev1..lev8`
  values were never a real relationship, so they weren't used for backfill).
- `apps/expenses/migrations/0003_expense_gl_account.py` — adds `Expense.gl_account`.
