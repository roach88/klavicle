import os

import pytest

from .client import KlaviyoClient


@pytest.fixture
def client():
    api_key = os.getenv("KLAVIYO_API_KEY")
    if not api_key:
        pytest.skip("KLAVIYO_API_KEY environment variable not set")
    return KlaviyoClient(api_key)


async def test_get_lists(client):
    """Test getting lists."""
    response = await client.get_lists()
    assert "data" in response


async def test_get_segments(client):
    """Test getting segments."""
    response = await client.get_segments()
    assert "data" in response


async def test_get_tags(client):
    """Test getting tags."""
    response = await client.get_tags()
    assert "data" in response


async def test_create_list(client):
    """Test creating a list."""
    response = await client.create_list("Test List", "Test Description")
    assert "data" in response
    assert response["data"]["attributes"]["name"] == "Test List"
