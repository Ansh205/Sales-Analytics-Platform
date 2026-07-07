"""
database.py

Creates SQLAlchemy engine for PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# =====================================
# PostgreSQL Configuration
# =====================================

DB_USER = "postgres"

DB_PASSWORD = "ansh1234"

DB_HOST = "localhost"

DB_PORT = "5432"

DB_NAME = "sales_analytics_db"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =====================================
# SQLAlchemy Engine
# =====================================

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# =====================================
# Session Factory
# =====================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)