# Bugs found during testing:
#
# Bug 1: schemas.py had pet name type defined as "integer" instead of "string".
#   The pet name field (e.g. "snowball", "ranger") is clearly a string, but the
#   schema incorrectly specified {"type": "integer"}, causing schema validation
#   to fail on valid API responses. Fixed by changing the type to "string".
#
# Bug 2: app.py findByStatus endpoint had a missing f-string prefix on the error
#   message for invalid status values. The line read 'Invalid pet status {status}'
#   instead of f'Invalid pet status {status}', causing it to print the literal
#   text "{status}" rather than the actual status value passed by the caller.
#   Fixed by adding the f-string prefix.

from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_


def test_pet_schema():
    test_endpoint = "/pets/1"

    response = api_helpers.get_api_data(test_endpoint)

    assert response.status_code == 200

    # Validate the response schema against the defined schema in schemas.py
    validate(instance=response.json(), schema=schemas.pet)


@pytest.mark.parametrize("status", ["available", "sold", "pending"])
def test_find_by_status_200(status):
    test_endpoint = "/pets/findByStatus"
    params = {
        "status": status
    }

    response = api_helpers.get_api_data(test_endpoint, params)

    assert_that(response.status_code, is_(200))

    pets = response.json()
    assert isinstance(pets, list), "Expected response to be a list"
    for pet in pets:
        assert_that(pet['status'], is_(status))
        validate(instance=pet, schema=schemas.pet)


@pytest.mark.parametrize("pet_id", [-1, 100, 999999, 2147483647])
def test_get_by_id_404(pet_id):
    test_endpoint = f"/pets/{pet_id}"

    response = api_helpers.get_api_data(test_endpoint)

    assert_that(response.status_code, is_(404))
