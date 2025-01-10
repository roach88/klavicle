from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.engine import Engine

metadata = MetaData(schema="tyler")

# Define the saved_queries table
saved_queries = Table(
    "saved_queries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("app_name", String(50), nullable=False, index=True),
    Column("name", String(255), nullable=False),
    Column("query_text", String, nullable=False),
    Column("description", String, nullable=True),
    Column("parameters", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    ),
    UniqueConstraint("app_name", "name", name="uq_app_name_query_name"),
    schema="tyler",
)


class QueryManager:
    """Manages SQL query execution and storage."""

    def __init__(self, engine: Engine, app_name: str = "klavicle"):
        """Initialize with database engine and app name."""
        self.engine = engine
        self.app_name = app_name
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
                app_name=self.app_name,
                name=name,
                description=description,
                query_text=query,
                parameters=params,
            )
            conn.execute(stmt)
            conn.commit()

    def load_query(self, name: str) -> tuple[str, Optional[dict]]:
        """Load a saved query by name."""
        with self.engine.connect() as conn:
            stmt = saved_queries.select().where(
                saved_queries.c.name == name, saved_queries.c.app_name == self.app_name
            )
            result = conn.execute(stmt).first()
            if not result:
                raise ValueError(
                    f"No query found with name: {name} for app: {self.app_name}"
                )
            return result.query_text, result.parameters

    def list_queries(self) -> list[dict]:
        """List all saved queries for the current app."""
        with self.engine.connect() as conn:
            stmt = saved_queries.select().where(
                saved_queries.c.app_name == self.app_name
            )
            result = conn.execute(stmt)
            return [dict(row) for row in result]

    def delete_query(self, name: str) -> None:
        """Delete a saved query by name."""
        with self.engine.connect() as conn:
            stmt = saved_queries.delete().where(
                saved_queries.c.name == name, saved_queries.c.app_name == self.app_name
            )
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
                .where(
                    saved_queries.c.name == name,
                    saved_queries.c.app_name == self.app_name,
                )
                .values(**updates)
            )
            conn.execute(stmt)
            conn.commit()
