"""
Unit tests for Core Analytics API endpoints & query filters (Phase 5.3 & Phase 5.4).
"""

import unittest
from fastapi.testclient import TestClient

from app.main import app


class TestAnalyticsAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # --------------------------------------------------
    # PHASE 5.3 BASE UNFILTERED ENDPOINT TESTS
    # --------------------------------------------------

    def test_read_root(self):
        """Verify root endpoint GET / is healthy."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "healthy")

    def test_health_check_db(self):
        """Verify database health endpoint GET /api/health/db."""
        response = self.client.get("/api/health/db")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("database"), "connected")

    def test_get_executive_summary(self):
        """Verify GET /api/summary returns correct structure and status 200."""
        response = self.client.get("/api/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        required_keys = {
            "total_sales",
            "total_profit",
            "total_orders",
            "total_customers",
            "profit_margin",
            "return_rate",
        }
        self.assertTrue(required_keys.issubset(data.keys()))
        self.assertIsInstance(data["total_sales"], (int, float))
        self.assertIsInstance(data["total_profit"], (int, float))
        self.assertIsInstance(data["total_orders"], int)
        self.assertIsInstance(data["total_customers"], int)

    def test_get_sales_summary(self):
        """Verify GET /api/sales/summary returns correct metrics and status 200."""
        response = self.client.get("/api/sales/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        required_keys = {
            "total_sales",
            "total_profit",
            "total_orders",
            "total_quantity",
            "average_order_value",
            "average_discount",
            "profit_margin",
        }
        self.assertTrue(required_keys.issubset(data.keys()))
        self.assertIsInstance(data["total_sales"], (int, float))
        self.assertIsInstance(data["total_orders"], int)
        self.assertIsInstance(data["total_quantity"], int)

    def test_get_monthly_sales(self):
        """Verify GET /api/sales/monthly returns chronological list of monthly data."""
        response = self.client.get("/api/sales/monthly")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first_item = data[0]
        required_keys = {"year", "month", "sales", "profit"}
        self.assertTrue(required_keys.issubset(first_item.keys()))

    def test_get_regional_sales(self):
        """Verify GET /api/sales/region returns list of regional metrics."""
        response = self.client.get("/api/sales/region")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first_item = data[0]
        required_keys = {"region", "sales", "profit", "orders"}
        self.assertTrue(required_keys.issubset(first_item.keys()))

    def test_get_top_products(self):
        """Verify GET /api/products/top returns top products by sales."""
        response = self.client.get("/api/products/top")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 10)

    def test_get_top_customers(self):
        """Verify GET /api/customers/top returns top customers by sales."""
        response = self.client.get("/api/customers/top")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 10)

    # --------------------------------------------------
    # PHASE 5.4 FILTER & VALIDATION TESTS
    # --------------------------------------------------

    def test_get_summary_filtered(self):
        """Verify GET /api/summary with year, region, category, segment filters."""
        response = self.client.get("/api/summary?year=2023&region=Central")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("total_sales", data)
        self.assertGreater(data["total_sales"], 0)

    def test_get_sales_summary_filtered(self):
        """Verify GET /api/sales/summary with filters."""
        response = self.client.get("/api/sales/summary?year=2022&region=East")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("total_sales", data)

    def test_get_monthly_sales_filtered_year(self):
        """Verify GET /api/sales/monthly?year=2023 returns only 2023 records."""
        response = self.client.get("/api/sales/monthly?year=2023")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for item in data:
            self.assertEqual(item["year"], 2023)

    def test_get_regional_sales_filtered(self):
        """Verify GET /api/sales/region with year and category filters."""
        response = self.client.get("/api/sales/region?year=2023&category=Technology")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_products_top_with_limit(self):
        """Verify GET /api/products/top?limit=5 returns at most 5 products."""
        response = self.client.get("/api/products/top?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)

    def test_get_products_top_category_filter(self):
        """Verify GET /api/products/top?category=Technology returns only Technology category."""
        response = self.client.get("/api/products/top?category=Technology&limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for item in data:
            self.assertEqual(item["category"], "Technology")

    def test_get_customers_top_segment_filter(self):
        """Verify GET /api/customers/top?segment=Consumer returns only Consumer segment."""
        response = self.client.get("/api/customers/top?segment=Consumer&limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for item in data:
            self.assertEqual(item["segment"], "Consumer")

    def test_non_existent_filter(self):
        """Verify query with non-existent filter value returns empty list gracefully."""
        response = self.client.get("/api/products/top?category=NonExistingCategory")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, [])

    # --------------------------------------------------
    # QUERY VALIDATION ERRORS (HTTP 422)
    # --------------------------------------------------

    def test_validation_limit_underflow(self):
        """Verify GET /api/products/top?limit=0 returns HTTP 422 Unprocessable Entity."""
        response = self.client.get("/api/products/top?limit=0")
        self.assertEqual(response.status_code, 422)

    def test_validation_limit_overflow(self):
        """Verify GET /api/products/top?limit=101 returns HTTP 422 Unprocessable Entity."""
        response = self.client.get("/api/products/top?limit=101")
        self.assertEqual(response.status_code, 422)

    def test_validation_invalid_year_type(self):
        """Verify GET /api/sales/monthly?year=abc returns HTTP 422 Unprocessable Entity."""
        response = self.client.get("/api/sales/monthly?year=abc")
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
