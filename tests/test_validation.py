import pytest
from klavicle.validation.handlers import (
    ValidationError,
    validate_list_data,
    validate_profile_data,
    validate_saved_query,
    validate_segment_data,
    validate_sql_query,
)


def test_validate_profile_data_valid():
    """Test validating valid profile data."""
    data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1-555-555-5555",
        "properties": {"custom_field": "value"},
    }
    validate_profile_data(data)  # Should not raise


def test_validate_profile_data_invalid_email():
    """Test validating profile data with invalid email."""
    data = {"email": "invalid-email", "first_name": "Test"}
    with pytest.raises(ValidationError):
        validate_profile_data(data)


def test_validate_profile_data_invalid_phone():
    """Test validating profile data with invalid phone number."""
    data = {"email": "test@example.com", "phone_number": "invalid-phone"}
    with pytest.raises(ValidationError):
        validate_profile_data(data)


def test_validate_list_data_valid():
    """Test validating valid list data."""
    data = {"name": "Test List", "description": "Test Description"}
    validate_list_data(data)  # Should not raise


def test_validate_list_data_invalid():
    """Test validating list data with empty name."""
    data = {"name": "", "description": "Test Description"}
    with pytest.raises(ValidationError):
        validate_list_data(data)


def test_validate_segment_data_valid():
    """Test validating valid segment data."""
    data = {
        "name": "Test Segment",
        "conditions": {
            "and": [
                {"property": "email", "operator": "equals", "value": "test@example.com"}
            ]
        },
    }
    validate_segment_data(data)  # Should not raise


def test_validate_segment_data_invalid():
    """Test validating segment data with empty name."""
    data = {"name": "", "conditions": {}}
    with pytest.raises(ValidationError):
        validate_segment_data(data)


def test_validate_sql_query_valid():
    """Test validating valid SQL query."""
    query = "SELECT * FROM test WHERE id = :id"
    result = validate_sql_query(query)
    assert result == query.strip()


def test_validate_sql_query_empty():
    """Test validating empty SQL query."""
    with pytest.raises(ValidationError):
        validate_sql_query("")


def test_validate_saved_query_valid():
    """Test validating valid saved query."""
    validate_saved_query(
        "test-query", "SELECT * FROM test", "Test query"
    )  # Should not raise


def test_validate_saved_query_empty_name():
    """Test validating saved query with empty name."""
    with pytest.raises(ValidationError):
        validate_saved_query("", "SELECT * FROM test", "Test query")
