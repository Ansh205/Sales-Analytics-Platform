"""
Unit tests for PostgreSQL database connection layer (Phase 5.2).
"""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine, get_db
from app.main import app


class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_engine_initialization(self):
        """Verify that SQLAlchemy engine initializes properly."""
        self.assertIsNotNone(engine)

    def test_get_db_session_lifecycle(self):
        """Verify get_db() yields session and closes properly."""
        generator = get_db()
        db = next(generator)
        try:
            result = db.execute(text("SELECT 1")).scalar()
            self.assertEqual(result, 1)
        finally:
            try:
                next(generator)
            except StopIteration:
                pass

    def test_health_check_db_endpoint(self):
        """Verify GET /api/health/db returns 200 OK and healthy status."""
        response = self.client.get("/api/health/db")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "healthy")
        self.assertEqual(json_data.get("database"), "connected")

    def test_current_database_name(self):
        """Verify that database connection connects specifically to sales_analytics_db."""
        generator = get_db()
        db = next(generator)
        try:
            db_name = db.execute(text("SELECT current_database();")).scalar()
            self.assertEqual(db_name, "sales_analytics_db")
        finally:
            try:
                next(generator)
            except StopIteration:
                pass

    def test_existing_tables_row_counts(self):
        """Verify that orders, returns, and people tables exist and row counts are unchanged."""
        generator = get_db()
        db = next(generator)
        try:
            orders_count = db.execute(text("SELECT COUNT(*) FROM orders;")).scalar()
            returns_count = db.execute(text("SELECT COUNT(*) FROM returns;")).scalar()
            people_count = db.execute(text("SELECT COUNT(*) FROM people;")).scalar()

            self.assertEqual(orders_count, 10194)
            self.assertEqual(returns_count, 800)
            self.assertEqual(people_count, 4)
        finally:
            try:
                next(generator)
            except StopIteration:
                pass


if __name__ == "__main__":
    unittest.main()
