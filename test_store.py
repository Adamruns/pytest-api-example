from jsonschema import validate
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
