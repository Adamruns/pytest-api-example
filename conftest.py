from jsonschema import validate
import pytest
import schemas
import api_helpers


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
