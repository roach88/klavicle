import pytest
from sqlalchemy import text

from .connection import create_db_connection
from .query_manager import QueryManager


@pytest.fixture
def query_manager():
    """Create a QueryManager instance for testing."""
    engine = create_db_connection()
    return QueryManager(engine)


def test_save_and_load_query(query_manager):
    """Test saving and loading a query."""
    name = "test_query"
    query = "SELECT * FROM users WHERE age > :min_age"
    params = {"min_age": 18}
    description = "Test query for users over 18"

    # Save query
    query_manager.save_query(name, query, description, params)

    # Load query
    loaded_query, loaded_params = query_manager.load_query(name)
    assert loaded_query == query
    assert loaded_params == params


def test_execute_query(query_manager):
    """Test executing a query."""
    # Create a test table
    with query_manager.engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER, value TEXT)")
        )
        conn.execute(text("INSERT INTO test_table VALUES (1, 'test')"))
        conn.commit()

    # Execute query
    result = query_manager.execute_query(
        "SELECT * FROM test_table WHERE id = :id", {"id": 1}
    )
    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["value"] == "test"

    # Clean up
    with query_manager.engine.connect() as conn:
        conn.execute(text("DROP TABLE test_table"))
        conn.commit()


def test_list_queries(query_manager):
    """Test listing saved queries."""
    # Save some test queries
    query_manager.save_query("query1", "SELECT 1")
    query_manager.save_query("query2", "SELECT 2")

    # List queries
    queries = query_manager.list_queries()
    assert len(queries) >= 2
    assert any(q["name"] == "query1" for q in queries)
    assert any(q["name"] == "query2" for q in queries)


def test_update_query(query_manager):
    """Test updating a saved query."""
    name = "update_test"
    query_manager.save_query(name, "SELECT 1")

    # Update query
    new_query = "SELECT 2"
    query_manager.update_query(name, query=new_query)

    # Verify update
    loaded_query, _ = query_manager.load_query(name)
    assert loaded_query == new_query


def test_delete_query(query_manager):
    """Test deleting a saved query."""
    name = "delete_test"
    query_manager.save_query(name, "SELECT 1")

    # Delete query
    query_manager.delete_query(name)

    # Verify deletion
    with pytest.raises(ValueError):
        query_manager.load_query(name)
