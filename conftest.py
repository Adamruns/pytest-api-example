from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, is_, greater_than


@pytest.fixture
def create_order():
    """Create a fresh order using an available pet, then restore the pet afterwards."""
    # Find an available pet
    response = api_helpers.get_api_data("/pets/findByStatus", {"status": "available"})
    assert_that(response.status_code, is_(200))
    available_pets = response.json()
    assert_that(len(available_pets), greater_than(0))

    pet_id = available_pets[0]['id']

    # Place a new order for that pet
    order_response = api_helpers.post_api_data("/store/order", {"pet_id": pet_id})
    assert_that(order_response.status_code, is_(201))

    order_data = order_response.json()
    validate(instance=order_data, schema=schemas.order)

    yield order_data

    # Teardown: restore the pet to "available" so subsequent tests
    # are not affected by state changes made during the test.
    order_id = order_data['id']
    api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": "available"})
