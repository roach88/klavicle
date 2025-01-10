import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .connection import create_db_connection


def test_create_db_connection():
    """Test database connection creation"""
    try:
        engine = create_db_connection()
        assert isinstance(engine, Engine)

        # Test connection by executing a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1

    except Exception as e:
        pytest.fail(f"Failed to create database connection: {str(e)}")


if __name__ == "__main__":
    test_create_db_connection()
