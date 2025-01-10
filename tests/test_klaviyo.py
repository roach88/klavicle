from unittest.mock import AsyncMock, patch

import pytest
from klavicle.klaviyo.client import KlaviyoClient


@pytest.fixture
def mock_klaviyo_sdk():
    """Create a mock Klaviyo SDK."""
    with patch("klavicle.klaviyo.client.Client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def klaviyo_client(mock_klaviyo_sdk):
    """Create a KlaviyoClient instance with mocked SDK."""
    return KlaviyoClient(api_key="test_api_key")


@pytest.mark.asyncio
async def test_get_profile(klaviyo_client, mock_klaviyo_sdk):
    """Test getting a profile."""
    mock_klaviyo_sdk.Profiles.get_profile.return_value = {
        "id": "123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    profile = await klaviyo_client.get_profile("123")
    assert profile["id"] == "123"
    assert profile["email"] == "test@example.com"
    mock_klaviyo_sdk.Profiles.get_profile.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_create_profile(klaviyo_client, mock_klaviyo_sdk):
    """Test creating a profile."""
    profile_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }
    mock_klaviyo_sdk.Profiles.create_profile.return_value = {
        "id": "123",
        **profile_data,
    }

    profile = await klaviyo_client.create_profile(profile_data)
    assert profile["id"] == "123"
    assert profile["email"] == "test@example.com"
    mock_klaviyo_sdk.Profiles.create_profile.assert_called_once()


@pytest.mark.asyncio
async def test_update_profile(klaviyo_client, mock_klaviyo_sdk):
    """Test updating a profile."""
    profile_data = {"first_name": "Updated", "last_name": "User"}
    mock_klaviyo_sdk.Profiles.update_profile.return_value = {
        "id": "123",
        **profile_data,
    }

    await klaviyo_client.update_profile("123", profile_data)
    mock_klaviyo_sdk.Profiles.update_profile.assert_called_once()


@pytest.mark.asyncio
async def test_get_lists(klaviyo_client, mock_klaviyo_sdk):
    """Test getting lists."""
    mock_klaviyo_sdk.Lists.get_lists.return_value = [
        {
            "id": "123",
            "name": "Test List",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        }
    ]

    lists = await klaviyo_client.get_lists()
    assert len(lists) == 1
    assert lists[0]["id"] == "123"
    assert lists[0]["name"] == "Test List"
    mock_klaviyo_sdk.Lists.get_lists.assert_called_once()


@pytest.mark.asyncio
async def test_create_list(klaviyo_client, mock_klaviyo_sdk):
    """Test creating a list."""
    list_data = {"name": "Test List", "description": "Test Description"}
    mock_klaviyo_sdk.Lists.create_list.return_value = {"id": "123", **list_data}

    list_item = await klaviyo_client.create_list(list_data)
    assert list_item["id"] == "123"
    assert list_item["name"] == "Test List"
    mock_klaviyo_sdk.Lists.create_list.assert_called_once()


@pytest.mark.asyncio
async def test_get_segments(klaviyo_client, mock_klaviyo_sdk):
    """Test getting segments."""
    mock_klaviyo_sdk.Segments.get_segments.return_value = [
        {
            "id": "123",
            "name": "Test Segment",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        }
    ]

    segments = await klaviyo_client.get_segments()
    assert len(segments) == 1
    assert segments[0]["id"] == "123"
    assert segments[0]["name"] == "Test Segment"
    mock_klaviyo_sdk.Segments.get_segments.assert_called_once()


@pytest.mark.asyncio
async def test_create_segment(klaviyo_client, mock_klaviyo_sdk):
    """Test creating a segment."""
    segment_data = {"name": "Test Segment", "conditions": {"field": "value"}}
    mock_klaviyo_sdk.Segments.create_segment.return_value = {
        "id": "123",
        **segment_data,
    }

    segment = await klaviyo_client.create_segment(segment_data)
    assert segment["id"] == "123"
    assert segment["name"] == "Test Segment"
    mock_klaviyo_sdk.Segments.create_segment.assert_called_once()


@pytest.mark.asyncio
async def test_get_tags(klaviyo_client, mock_klaviyo_sdk):
    """Test getting tags."""
    mock_klaviyo_sdk.Tags.get_tags.return_value = [
        {
            "id": "123",
            "name": "test-tag",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        }
    ]

    tags = await klaviyo_client.get_tags()
    assert len(tags) == 1
    assert tags[0]["id"] == "123"
    assert tags[0]["name"] == "test-tag"
    mock_klaviyo_sdk.Tags.get_tags.assert_called_once()


@pytest.mark.asyncio
async def test_add_tags(klaviyo_client, mock_klaviyo_sdk):
    """Test adding tags."""
    await klaviyo_client.add_tags("profile", "123", ["tag1", "tag2"])
    mock_klaviyo_sdk.Tags.create_tag_relationships.assert_called_once()


@pytest.mark.asyncio
async def test_remove_tags(klaviyo_client, mock_klaviyo_sdk):
    """Test removing tags."""
    await klaviyo_client.remove_tags("profile", "123", ["tag1", "tag2"])
    mock_klaviyo_sdk.Tags.delete_tag_relationships.assert_called_once()
