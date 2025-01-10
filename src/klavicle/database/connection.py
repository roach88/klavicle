import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL


def create_db_connection() -> Engine:
    """Create database connection using environment variables"""
    load_dotenv()  # Load environment variables from .env file

    drivername = os.getenv("DB_DRIVERNAME")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    if not all([drivername, username, password]):
        raise ValueError("Missing required database environment variables")

    return create_engine(
        URL.create(
            drivername=str(drivername),
            username=str(username),
            password=str(password),
            host=os.getenv("DB_HOST") or "localhost",
            port=int(os.getenv("DB_PORT", "0")) if os.getenv("DB_PORT") else None,
            database=os.getenv("DB_DATABASE") or "",
            query={"sslmode": "require"},
        )
    )
