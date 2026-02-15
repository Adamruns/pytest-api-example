# Bugs found during testing are documented in BUGS.md

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


def test_find_by_status_400_invalid_status():
    """Regression test for Bug 2: invalid status error message includes the actual value.

    The original code used a plain string instead of an f-string, so the error
    message contained the literal text '{status}' instead of the submitted value.
    See BUGS.md for details.
    """
    invalid_status = "nonexistent_status"
    response = api_helpers.get_api_data("/pets/findByStatus", {"status": invalid_status})

    assert_that(response.status_code, is_(400))
    assert_that(response.json()["message"], contains_string(invalid_status))
