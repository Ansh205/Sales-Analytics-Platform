"""
test_ml.py

Unit and Integration Tests for Machine Learning Pipeline, Preprocessing,
Leakage Prevention, and API Endpoints.
"""

import unittest
from pathlib import Path
from fastapi.testclient import TestClient
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from app.main import app
from scripts.ml.train_profit_model import (
    CATEGORICAL_FEATURES,
    LEAKAGE_AND_ID_COLUMNS,
    NUMERICAL_FEATURES,
    TARGET_COLUMN,
    build_preprocessor,
    create_model_pipelines,
    prepare_data,
)


class TestMachineLearningPipeline(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Create minimal synthetic dataset resembling orders_clean.csv
        np.random.seed(42)
        n = 100
        self.synthetic_df = pd.DataFrame({
            "Row ID": range(1, n + 1),
            "Order ID": [f"CA-2023-{1000 + i}" for i in range(n)],
            "Sales": np.random.uniform(10, 1000, n),
            "Quantity": np.random.randint(1, 10, n),
            "Discount": np.random.choice([0.0, 0.1, 0.2, 0.4, 0.7], n),
            "Profit": np.random.uniform(-200, 300, n),
            "Category": np.random.choice(["Furniture", "Office Supplies", "Technology"], n),
            "Sub-Category": np.random.choice(["Chairs", "Paper", "Phones", "Binders"], n),
            "Segment": np.random.choice(["Consumer", "Corporate", "Home Office"], n),
            "Region": np.random.choice(["Central", "East", "South", "West"], n),
            "Ship Mode": np.random.choice(["Standard Class", "First Class"], n),
            "Order Month": np.random.choice(["January", "July", "December"], n),
            "Profit Margin": np.random.uniform(-0.5, 0.5, n),
            "Profit Bucket": np.random.choice(["Loss", "Low Profit", "High Profit"], n),
            "Customer ID": [f"CUST-{i}" for i in range(n)],
            "Customer Name": [f"Customer {i}" for i in range(n)],
            "Product ID": [f"PROD-{i}" for i in range(n)],
            "Product Name": [f"Product {i}" for i in range(n)],
            "Ship Date": pd.date_range("2023-01-01", periods=n),
            "Shipping Days": np.random.randint(1, 7, n),
        })

    def test_prepare_data_leakage_prevention(self):
        """Verify that target and leakage columns are strictly excluded from feature sets."""
        X_train, X_test, y_train, y_test = prepare_data(self.synthetic_df, test_size=0.20, random_state=42)

        self.assertEqual(len(X_train), 80)
        self.assertEqual(len(X_test), 20)
        self.assertEqual(len(y_train), 80)
        self.assertEqual(len(y_test), 20)

        # Check target is excluded from X
        self.assertNotIn(TARGET_COLUMN, X_train.columns)
        self.assertNotIn(TARGET_COLUMN, X_test.columns)

        # Check all leakage columns are excluded
        for col in LEAKAGE_AND_ID_COLUMNS:
            self.assertNotIn(col, X_train.columns)
            self.assertNotIn(col, X_test.columns)

        # Check only permitted features are present
        expected_cols = set(NUMERICAL_FEATURES + CATEGORICAL_FEATURES)
        self.assertEqual(set(X_train.columns), expected_cols)

    def test_preprocessor_column_transformer(self):
        """Verify ColumnTransformer transforms features and handles unseen categories."""
        preprocessor = build_preprocessor()
        X = self.synthetic_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]

        transformed = preprocessor.fit_transform(X)
        self.assertIsInstance(transformed, np.ndarray)
        self.assertEqual(transformed.shape[0], len(X))

        # Test with out-of-vocabulary category
        unseen_data = X.iloc[:2].copy()
        unseen_data.loc[0, "Category"] = "UnseenNewCategory"
        transformed_unseen = preprocessor.transform(unseen_data)
        self.assertEqual(transformed_unseen.shape[1], transformed.shape[1])

    def test_model_pipeline_training_and_scoring(self):
        """Verify that models fit and produce finite test predictions."""
        X_train, X_test, y_train, y_test = prepare_data(self.synthetic_df, test_size=0.20, random_state=42)
        models = create_model_pipelines(random_state=42)

        for name, pipe in models.items():
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            self.assertEqual(len(preds), len(X_test))
            self.assertFalse(np.isnan(preds).any(), f"NaN found in predictions for {name}")

    def test_negative_r2_handling(self):
        """Verify that negative R2 is mathematically computed without throwing errors."""
        y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        # Horrible predictions that are far worse than predicting mean (30.0)
        y_terrible_pred = np.array([500.0, -400.0, 300.0, -200.0, 1000.0])
        r2 = r2_score(y_true, y_terrible_pred)
        self.assertLess(r2, 0.0)
        self.assertTrue(np.isfinite(r2))

    def test_api_ml_summary_endpoint(self):
        """Verify GET /api/ml/summary returns HTTP 200 and experiment sections."""
        response = self.client.get("/api/ml/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("models_comparison", data)
        self.assertIn("experiment_config", data)
        self.assertIn("statistical_hypothesis", data)

    def test_api_ml_predict_endpoint_success(self):
        """Verify POST /api/ml/predict generates valid profit prediction."""
        payload = {
            "sales": 250.0,
            "quantity": 2,
            "discount": 0.10,
            "category": "Technology",
            "sub_category": "Phones",
            "segment": "Consumer",
            "region": "West",
            "ship_mode": "Standard Class",
            "order_month": "March"
        }
        response = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("predicted_profit", data)
        self.assertIn("is_predicted_loss", data)
        self.assertIn("risk_level", data)
        self.assertIsInstance(data["predicted_profit"], (int, float))
        self.assertIsInstance(data["is_predicted_loss"], bool)

    def test_api_ml_predict_validation_errors(self):
        """Verify POST /api/ml/predict returns HTTP 422 for invalid payloads."""
        # Case 1: Negative sales
        bad_sales = {
            "sales": -50.0,
            "quantity": 2,
            "discount": 0.1,
            "category": "Technology",
            "sub_category": "Phones"
        }
        res1 = self.client.post("/api/ml/predict", json=bad_sales)
        self.assertEqual(res1.status_code, 422)

        # Case 2: Discount > 1.0
        bad_discount = {
            "sales": 100.0,
            "quantity": 1,
            "discount": 1.5,
            "category": "Furniture",
            "sub_category": "Chairs"
        }
        res2 = self.client.post("/api/ml/predict", json=bad_discount)
        self.assertEqual(res2.status_code, 422)

    def test_render_ml_page(self):
        """Verify GET /ml returns HTTP 200 with HTML content containing prediction and hypothesis sections."""
        response = self.client.get("/ml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Machine Learning", response.text)
        self.assertIn("Predictive Intelligence", response.text)
        self.assertIn("Interactive Order Profit Scoring", response.text)
        self.assertIn("Statistical Hypothesis Testing", response.text)


if __name__ == "__main__":
    unittest.main()
