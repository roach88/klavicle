import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Load environment variables from .env file if it exists
    load_dotenv()

    # Set test environment variables
    os.environ["KLAVIYO_API_KEY"] = "test_api_key"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = "test_db"
    os.environ["DB_USER"] = "test_user"
    os.environ["DB_PASSWORD"] = "test_password"

    yield

    # Clean up environment variables
    for var in [
        "KLAVIYO_API_KEY",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]:
        os.environ.pop(var, None)
