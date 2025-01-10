import json
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner
from klavicle.cli.commands import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_klaviyo_client():
    """Create a mock KlaviyoClient."""
    with patch("klavicle.cli.klaviyo_commands.get_klaviyo_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_query_manager():
    """Create a mock QueryManager."""
    with patch("klavicle.cli.query_commands.get_query_manager") as mock:
        manager = AsyncMock()
        mock.return_value = manager
        yield manager


def test_query_list(runner, mock_query_manager):
    """Test listing saved queries."""
    mock_query_manager.list_queries.return_value = [
        {
            "name": "test-query",
            "description": "Test query",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01",
        }
    ]

    result = runner.invoke(cli, ["query", "list"])
    assert result.exit_code == 0
    assert "test-query" in result.output
    assert "Test query" in result.output


def test_query_save(runner, mock_query_manager):
    """Test saving a query."""
    result = runner.invoke(
        cli,
        [
            "query",
            "save",
            "test-query",
            "SELECT * FROM test",
            "--description",
            "Test query",
        ],
    )

    assert result.exit_code == 0
    assert "saved successfully" in result.output
    mock_query_manager.save_query.assert_called_once_with(
        "test-query", "SELECT * FROM test", "Test query"
    )


@pytest.mark.asyncio
async def test_profile_get(runner, mock_klaviyo_client):
    """Test getting a profile."""
    mock_klaviyo_client.get_profile.return_value = {
        "id": "123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    result = runner.invoke(cli, ["profile", "get", "123"])
    assert result.exit_code == 0
    assert "test@example.com" in result.output
    assert "Test" in result.output
    assert "User" in result.output


@pytest.mark.asyncio
async def test_profile_create(runner, mock_klaviyo_client):
    """Test creating a profile."""
    profile_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }
    mock_klaviyo_client.create_profile.return_value = {"id": "123", **profile_data}

    result = runner.invoke(cli, ["profile", "create", json.dumps(profile_data)])

    assert result.exit_code == 0
    assert "created successfully" in result.output
    mock_klaviyo_client.create_profile.assert_called_once_with(profile_data)


@pytest.mark.asyncio
async def test_list_get(runner, mock_klaviyo_client):
    """Test getting lists."""
    mock_klaviyo_client.get_lists.return_value = [
        {
            "id": "123",
            "name": "Test List",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        }
    ]

    result = runner.invoke(cli, ["list", "list"])
    assert result.exit_code == 0
    assert "Test List" in result.output


@pytest.mark.asyncio
async def test_segment_get(runner, mock_klaviyo_client):
    """Test getting segments."""
    mock_klaviyo_client.get_segments.return_value = [
        {
            "id": "123",
            "name": "Test Segment",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        }
    ]

    result = runner.invoke(cli, ["segment", "list"])
    assert result.exit_code == 0
    assert "Test Segment" in result.output


@pytest.mark.asyncio
async def test_tag_get(runner, mock_klaviyo_client):
    """Test getting tags."""
    mock_klaviyo_client.get_tags.return_value = [
        {
            "id": "123",
            "name": "test-tag",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        }
    ]

    result = runner.invoke(cli, ["tag", "list"])
    assert result.exit_code == 0
    assert "test-tag" in result.output
