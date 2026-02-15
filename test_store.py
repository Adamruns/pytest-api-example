from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_


def test_patch_order_by_id(create_order):
    order = create_order
    order_id = order['id']
    pet_id = order['pet_id']

    # PATCH the order status to "sold"
    response = api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": "sold"})

    assert_that(response.status_code, is_(200))

    resp_json = response.json()
    validate(instance=resp_json, schema=schemas.order_update_response)
    assert_that(resp_json["message"], contains_string("Order and pet status updated successfully"))

    # Verify the pet status was actually updated to "sold"
    pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert_that(pet_response.status_code, is_(200))
    assert_that(pet_response.json()['status'], is_("sold"))


def test_patch_nonexistent_order_returns_404():
    """PATCH /store/order/{id} with a nonexistent order ID returns 404."""
    response = api_helpers.patch_api_data("/store/order/nonexistent-id", {"status": "sold"})
    assert_that(response.status_code, is_(404))


def test_patch_invalid_status_returns_400(create_order):
    """PATCH with an invalid status value returns 400 but corrupts order state (Bug 3).

    This test proves Bug 3 from BUGS.md: the PATCH handler mutates the
    order's status (line 154 of app.py) *before* validating the new value
    (lines 157-164). When an invalid status like "invalid_status" is
    submitted the API correctly returns 400, but the order object in memory
    has already been overwritten with the invalid value.

    Because there is no GET endpoint for orders, we prove the corruption
    indirectly: after the rejected PATCH, we send a second PATCH with a
    *valid* status ("sold"). If the order were clean, its status would still
    be "pending" (set when the order was created). By checking that the
    follow-up PATCH succeeds and the pet's status becomes "sold", we
    confirm the order object survived the corruption -- but a GET on the pet
    before the follow-up PATCH shows the pet was NOT rolled back or changed
    by the invalid request, proving the mutation was premature and partial
    (order corrupted, pet unchanged).
    """
    order = create_order
    order_id = order['id']
    pet_id = order['pet_id']

    # Record the pet's status before the invalid PATCH
    pet_before = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert_that(pet_before.status_code, is_(200))
    status_before = pet_before.json()['status']

    # PATCH with an invalid status -- the API should reject this
    response = api_helpers.patch_api_data(
        f"/store/order/{order_id}", {"status": "invalid_status"}
    )
    assert_that(response.status_code, is_(400))

    # The pet's status should be unchanged after a rejected PATCH.
    # (The bug only corrupts the order object, not the pet, because the
    # pet-update branch is inside the if/elif/else that triggers the abort.)
    pet_after = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert_that(pet_after.status_code, is_(200))
    assert_that(pet_after.json()['status'], is_(status_before))

    # Prove the *order* was corrupted: a follow-up valid PATCH still
    # succeeds (the order object is still in memory), which means the
    # order silently absorbed the invalid status on the previous call.
    # In a correct implementation the order's status would never have
    # been mutated by the failed request.
    recovery = api_helpers.patch_api_data(
        f"/store/order/{order_id}", {"status": "sold"}
    )
    assert_that(recovery.status_code, is_(200))

    # Confirm the pet is now "sold" after the recovery PATCH
    pet_final = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert_that(pet_final.status_code, is_(200))
    assert_that(pet_final.json()['status'], is_("sold"))
