"""
Database configuration and session management.
"""
import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./purchase_tracker.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)


def create_db_and_tables():
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Session: SQLModel session
    """
    with Session(engine) as session:
        yield session
