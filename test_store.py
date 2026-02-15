from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_


@pytest.fixture
def create_order():
    """Create a fresh order using an available pet."""
    # Find an available pet
    response = api_helpers.get_api_data("/pets/findByStatus", {"status": "available"})
    assert response.status_code == 200
    available_pets = response.json()
    assert len(available_pets) > 0, "No available pets to create an order"

    pet_id = available_pets[0]['id']

    # Place a new order for that pet
    order_response = api_helpers.post_api_data("/store/order", {"pet_id": pet_id})
    assert order_response.status_code == 201

    order_data = order_response.json()
    validate(instance=order_data, schema=schemas.order)

    return order_data


def test_patch_order_by_id(create_order):
    order = create_order
    order_id = order['id']
    pet_id = order['pet_id']

    # PATCH the order status to "sold"
    response = api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": "sold"})

    assert_that(response.status_code, is_(200))

    resp_json = response.json()
    assert_that(resp_json["message"], contains_string("Order and pet status updated successfully"))

    # Verify the pet status was actually updated to "sold"
    pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert_that(pet_response.status_code, is_(200))
    assert_that(pet_response.json()['status'], is_("sold"))
