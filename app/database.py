"""
PostgreSQL Database Connection Layer for Sales Analytics Platform API.

Provides single-instance SQLAlchemy engine with connection pooling,
session factory, and FastAPI dependency injection for database sessions.
"""

import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Fallback default connection string if DATABASE_URL is not set
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg2://postgres:ansh1234@localhost:5432/sales_analytics_db"
)

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Initialize single SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

# Session factory for generating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a SQLAlchemy database session.
    Ensures the session is cleanly closed after each request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
