from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy.engine import Engine

metadata = MetaData()

# Define the saved_queries table
saved_queries = Table(
    "saved_queries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("description", String, nullable=True),
    Column("query_text", String, nullable=False),
    Column("parameters", JSON, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)


class QueryManager:
    """Manages SQL query execution and storage."""

    def __init__(self, engine: Engine):
        """Initialize with database engine."""
        self.engine = engine
        metadata.create_all(engine)  # Create tables if they don't exist

    def execute_query(self, query: str, params: Optional[dict] = None) -> list[dict]:
        """Execute a query and return results as list of dicts."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return [dict(row) for row in result]

    def save_query(
        self,
        name: str,
        query: str,
        description: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> None:
        """Save a query for later use."""
        with self.engine.connect() as conn:
            stmt = saved_queries.insert().values(
                name=name, description=description, query_text=query, parameters=params
            )
            conn.execute(stmt)
            conn.commit()

    def load_query(self, name: str) -> tuple[str, Optional[dict]]:
        """Load a saved query by name."""
        with self.engine.connect() as conn:
            stmt = saved_queries.select().where(saved_queries.c.name == name)
            result = conn.execute(stmt).first()
            if not result:
                raise ValueError(f"No query found with name: {name}")
            return result.query_text, result.parameters

    def list_queries(self) -> list[dict]:
        """List all saved queries."""
        with self.engine.connect() as conn:
            stmt = saved_queries.select()
            result = conn.execute(stmt)
            return [dict(row) for row in result]

    def delete_query(self, name: str) -> None:
        """Delete a saved query by name."""
        with self.engine.connect() as conn:
            stmt = saved_queries.delete().where(saved_queries.c.name == name)
            conn.execute(stmt)
            conn.commit()

    def update_query(
        self,
        name: str,
        query: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> None:
        """Update a saved query."""
        updates = {}
        if query is not None:
            updates["query_text"] = query
        if description is not None:
            updates["description"] = description
        if params is not None:
            updates["parameters"] = params

        if not updates:
            return

        with self.engine.connect() as conn:
            stmt = (
                saved_queries.update()
                .where(saved_queries.c.name == name)
                .values(**updates)
            )
            conn.execute(stmt)
            conn.commit()
