import pytest
from klavicle.database.connection import create_db_connection
from klavicle.database.query_manager import QueryManager
from sqlalchemy.engine import Engine


def test_create_db_connection():
    """Test creating a database connection."""
    engine = create_db_connection()
    assert isinstance(engine, Engine)


@pytest.fixture
def query_manager():
    """Create a QueryManager instance."""
    engine = create_db_connection()
    return QueryManager(engine)


def test_query_manager_save_load(query_manager):
    """Test saving and loading a query."""
    # Save a query
    query_manager.save_query("test-query", "SELECT * FROM test", "Test query")

    # Load the query
    query_text, params = query_manager.load_query("test-query")
    assert query_text == "SELECT * FROM test"
    assert params == {}


def test_query_manager_list(query_manager):
    """Test listing saved queries."""
    # Save some queries
    query_manager.save_query("query1", "SELECT 1", "Query 1")
    query_manager.save_query("query2", "SELECT 2", "Query 2")

    # List queries
    queries = query_manager.list_queries()
    assert len(queries) >= 2

    # Check query data
    query_names = [q["name"] for q in queries]
    assert "query1" in query_names
    assert "query2" in query_names


def test_query_manager_execute(query_manager):
    """Test executing a query."""
    # Create a test table
    query_manager.execute_query(
        """
        CREATE TABLE IF NOT EXISTS test (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
    """
    )

    # Insert test data
    query_manager.execute_query(
        """
        INSERT INTO test (name) VALUES (:name)
    """,
        {"name": "Test"},
    )

    # Query test data
    results = query_manager.execute_query("SELECT * FROM test")
    assert len(results) == 1
    assert results[0]["name"] == "Test"

    # Clean up
    query_manager.execute_query("DROP TABLE test")
