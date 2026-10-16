"""
ml.py

Machine Learning and Statistical Inference API Endpoints.
Exposes saved ML model comparison, experiment metadata, statistical hypothesis test results,
and provides single-order profit prediction using the pre-trained best pipeline.
No models are retrained on request.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/ml", tags=["Machine Learning & Statistics"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "reports"
MODEL_PATH = REPORTS_DIR / "models" / "best_profit_model.joblib"
METRICS_PATH = REPORTS_DIR / "model_comparison.json"
CONFIG_PATH = REPORTS_DIR / "experiment_config.json"
STATS_PATH = REPORTS_DIR / "statistical_hypothesis_results.json"

# In-memory cached model singleton
_MODEL_CACHE: Optional[Any] = None


def get_cached_model():
    """
    Loads and caches the pre-trained model pipeline singleton.
    Avoids expensive file I/O and deserialization on every HTTP request.
    """
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Trained ML model artifact not found. Please run scripts/ml/train_profit_model.py first."
            )
        try:
            _MODEL_CACHE = joblib.load(MODEL_PATH)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load ML model: {str(e)}"
            )
    return _MODEL_CACHE


# Pydantic Schemas
class OrderPredictionRequest(BaseModel):
    sales: float = Field(..., gt=0, description="Gross order sales in USD (> 0)")
    quantity: int = Field(..., gt=0, description="Units ordered (>= 1)")
    discount: float = Field(..., ge=0.0, le=1.0, description="Discount rate between 0.0 and 1.0")
    category: str = Field(..., description="Product category (e.g., Furniture, Technology, Office Supplies)")
    sub_category: str = Field(..., description="Product sub-category (e.g., Chairs, Phones, Paper)")
    segment: str = Field(default="Consumer", description="Customer segment (Consumer, Corporate, Home Office)")
    region: str = Field(default="Central", description="Geographic region (Central, East, South, West)")
    ship_mode: str = Field(default="Standard Class", description="Shipping mode")
    order_month: str = Field(default="January", description="Month of order placement")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sales": 350.0,
                "quantity": 3,
                "discount": 0.15,
                "category": "Technology",
                "sub_category": "Phones",
                "segment": "Consumer",
                "region": "East",
                "ship_mode": "Standard Class",
                "order_month": "March"
            }
        }
    }


class OrderPredictionResponse(BaseModel):
    predicted_profit: float
    is_predicted_loss: bool
    risk_level: str
    model_name: str
    model_version: str


@router.get("/summary", summary="Retrieve ML and Statistical Experiment Summary")
def get_ml_experiment_summary() -> Dict[str, Any]:
    """
    Returns precomputed model comparison metrics, cross-validation scores,
    experiment configuration, and statistical hypothesis test results.
    """
    result: Dict[str, Any] = {}

    # 1. Model comparison
    if METRICS_PATH.exists():
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                result["models_comparison"] = json.load(f)
        except Exception as e:
            result["models_comparison_error"] = str(e)
    else:
        result["models_comparison"] = "Artifact pending"

    # 2. Experiment config
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                result["experiment_config"] = json.load(f)
        except Exception as e:
            result["experiment_config_error"] = str(e)

    # 3. Statistical hypothesis test
    if STATS_PATH.exists():
        try:
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                result["statistical_hypothesis"] = json.load(f)
        except Exception as e:
            result["statistical_hypothesis_error"] = str(e)

    return result


@router.post("/predict", response_model=OrderPredictionResponse, summary="Predict Order Profit")
def predict_order_profit(payload: OrderPredictionRequest) -> OrderPredictionResponse:
    """
    Predicts expected order net profit using the pre-trained HistGradientBoosting pipeline.
    Applies real-time margin risk classification.
    """
    model = get_cached_model()

    # Create input DataFrame with correct column names
    input_df = pd.DataFrame([{
        "Sales": payload.sales,
        "Quantity": payload.quantity,
        "Discount": payload.discount,
        "Category": payload.category.title(),
        "Sub-Category": payload.sub_category.title(),
        "Segment": payload.segment.title(),
        "Region": payload.region.title(),
        "Ship Mode": payload.ship_mode.title(),
        "Order Month": payload.order_month.title(),
    }])

    try:
        pred_profit = float(model.predict(input_df)[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Inference failed with provided features: {str(e)}"
        )

    is_loss = pred_profit < 0.0
    if is_loss:
        risk = "HIGH_MARGIN_RISK (Negative Expected Profit)"
    elif pred_profit < 20.0:
        risk = "MODERATE_MARGIN (Low Profitability)"
    else:
        risk = "HEALTHY_MARGIN"

    return OrderPredictionResponse(
        predicted_profit=round(pred_profit, 2),
        is_predicted_loss=is_loss,
        risk_level=risk,
        model_name="HistGradientBoostingRegressor",
        model_version="1.0.0"
    )
