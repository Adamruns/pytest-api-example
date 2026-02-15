# Bugs Found

## Bug 1: Incorrect schema type in `schemas.py` — FIXED

- **File:** `schemas.py`, line 9
- **Severity:** High — blocks `test_pet_schema` from passing
- **Description:** The `pet` schema defined the `name` property as `{"type": "integer"}` instead of `{"type": "string"}`. Pet names are strings (e.g. `"snowball"`, `"ranger"`), so `jsonschema.validate` correctly rejects every valid API response.
- **Expected:** `"type": "string"`
- **Actual:** `"type": "integer"`
- **Fix:** Changed the type to `"string"` in `schemas.py`.

## Bug 2: Missing f-string prefix in `app.py` — FIXED

- **File:** `app.py`, line 101
- **Severity:** Medium — error messages are misleading but the API still functions
- **Description:** The `findByStatus` endpoint's 400 error message was a plain string `'Invalid pet status {status}'` instead of an f-string `f'Invalid pet status {status}'`. When an invalid status is submitted, the error response contains the literal text `{status}` rather than the actual value.
- **Expected:** `f'Invalid pet status {status}'` → e.g. `"Invalid pet status xyz"`
- **Actual:** `'Invalid pet status {status}'` → literally `"Invalid pet status {status}"`
- **Fix:** Added the `f` prefix to the string.

## Bug 3: Premature state mutation in PATCH handler — NOT FIXED (design flaw)

- **File:** `app.py`, lines 154–164
- **Severity:** Medium — can corrupt in-memory data on invalid input
- **Description:** The `PATCH /store/order/{order_id}` handler mutates the order's status on line 154 (`order['status'] = update_data['status']`) **before** validating that the status value is one of the allowed values (`available`, `sold`, `pending`). If an invalid status like `"shipped"` is submitted, the order object is permanently corrupted with the invalid value even though the API returns 400.
- **Expected:** Validate the status value first, then mutate the order only if valid.
- **Actual:** Order is mutated immediately, validation happens after, and the 400 response does not roll back the mutation.
- **Impact:** Subsequent reads of the order will show the invalid status. In a persistent datastore this would be data corruption. In this in-memory implementation, it persists until server restart.
- **Not fixed** because modifying the system under test is outside the scope of the test tasks. Documented here for the reviewer.

## Bug 4: PATCH handler missing `available` status branch — FIXED

- **File:** `app.py`, lines 157–164
- **Severity:** Medium — valid status rejected as invalid
- **Description:** The `PATCH /store/order/{order_id}` handler only handled `pending` and `sold` in its status-update branches, falling through to the `else` → 400 error for `available`. Since `available` is a valid member of `PET_STATUS`, attempting to patch an order back to `available` would incorrectly return `400 Invalid status`.
- **Expected:** PATCH with `{"status": "available"}` should succeed and update the pet's status to `available`.
- **Actual:** The request fell through to the `else` branch and returned 400.
- **Fix:** Added an `elif update_data['status'] == 'available'` branch to update the pet's status accordingly.
