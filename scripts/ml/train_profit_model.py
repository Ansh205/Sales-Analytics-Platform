"""
train_profit_model.py

Order-Level Profit Prediction Machine Learning Experiment.
Target: Profit.
Compares:
1. Mean-prediction Baseline (DummyRegressor)
2. Regularized Linear Regression (Ridge)
3. Tree-based Gradient Boosting (HistGradientBoostingRegressor)
4. Tree-based Ensemble (RandomForestRegressor)

Uses scikit-learn Pipeline and ColumnTransformer.
Performs 5-Fold Cross Validation on the 80% training split and held-out evaluation on 20% test split.
Generates evaluation metrics (MAE, RMSE, R2), residual analysis, actual-vs-predicted plots,
feature importances, and serialized model artifacts.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# Exact features to use and prevent data leakage
NUMERICAL_FEATURES = ["Sales", "Quantity", "Discount"]
CATEGORICAL_FEATURES = ["Category", "Sub-Category", "Segment", "Region", "Ship Mode", "Order Month"]
TARGET_COLUMN = "Profit"

# Explicitly documented excluded columns
LEAKAGE_AND_ID_COLUMNS = [
    "Profit",          # Target
    "Profit Margin",   # Direct mathematical leak (Profit / Sales)
    "Profit Bucket",   # Derived from profit
    "Row ID",          # Arbitrary index
    "Order ID",        # High cardinality ID
    "Customer ID",     # Memorization leak
    "Customer Name",   # High cardinality text
    "Product ID",      # Memorization leak
    "Product Name",    # High cardinality text
    "Ship Date",       # Post-order fulfillment
    "Shipping Days",   # Post-order fulfillment
]


def prepare_data(df: pd.DataFrame, test_size: float = 0.20, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Validates input features, isolates target, and performs train/test split.
    Guarantees no target leakage into feature matrices.
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset.")

    missing_num = [c for c in NUMERICAL_FEATURES if c not in df.columns]
    missing_cat = [c for c in CATEGORICAL_FEATURES if c not in df.columns]
    if missing_num or missing_cat:
        raise ValueError(f"Missing expected features: Num={missing_num}, Cat={missing_cat}")

    # Extract target and features
    y = df[TARGET_COLUMN].copy()
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()

    # Split into train (80%) and held-out test (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, shuffle=True
    )

    return X_train, X_test, y_train, y_test


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs a ColumnTransformer that scales numerical variables and
    one-hot encodes categorical variables with out-of-vocabulary handling.
    """
    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop"
    )
    return preprocessor


def create_model_pipelines(random_state: int = 42) -> Dict[str, Pipeline]:
    """
    Instantiates candidate model pipelines with standard preprocessing.
    """
    preprocessor = build_preprocessor()

    models = {
        "Baseline (Mean Predictor)": Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", DummyRegressor(strategy="mean"))
        ]),
        "Regularized Linear Regression (Ridge)": Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=10.0, random_state=random_state))
        ]),
        "Tree-based (HistGradientBoosting)": Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", HistGradientBoostingRegressor(
                loss="squared_error",
                max_iter=150,
                max_leaf_nodes=31,
                min_samples_leaf=20,
                learning_rate=0.1,
                random_state=random_state
            ))
        ]),
        "Tree-based (Random Forest)": Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_leaf=5,
                random_state=random_state,
                n_jobs=-1
            ))
        ])
    }
    return models


def evaluate_models(
    models: Dict[str, Pipeline],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    cv_folds: int = 5,
    random_state: int = 42
) -> Tuple[pd.DataFrame, Dict[str, Pipeline], Dict[str, np.ndarray]]:
    """
    Performs 5-Fold Cross Validation on the training data and evaluates on the held-out test set.
    """
    results = []
    trained_models = {}
    test_predictions = {}
    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    scoring = {
        "mae": "neg_mean_absolute_error",
        "mse": "neg_mean_squared_error",
        "r2": "r2",
    }

    for name, pipeline in models.items():
        print(f"Evaluating {name}...")

        # 1. Cross Validation on training set
        cv_res = cross_validate(pipeline, X_train, y_train, cv=kf, scoring=scoring, n_jobs=-1)
        cv_mae_mean = -cv_res["test_mae"].mean()
        cv_mae_std = cv_res["test_mae"].std()
        cv_rmse_mean = np.sqrt(-cv_res["test_mse"]).mean()
        cv_rmse_std = np.sqrt(-cv_res["test_mse"]).std()
        cv_r2_mean = cv_res["test_r2"].mean()
        cv_r2_std = cv_res["test_r2"].std()

        # 2. Fit on entire training set
        pipeline.fit(X_train, y_train)
        trained_models[name] = pipeline

        # 3. Predict on held-out test set
        y_pred = pipeline.predict(X_test)
        test_predictions[name] = y_pred

        test_mae = mean_absolute_error(y_test, y_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        test_r2 = r2_score(y_test, y_pred)

        results.append({
            "Model": name,
            "CV_MAE_Mean": round(cv_mae_mean, 2),
            "CV_MAE_Std": round(cv_mae_std, 2),
            "CV_RMSE_Mean": round(cv_rmse_mean, 2),
            "CV_RMSE_Std": round(cv_rmse_std, 2),
            "CV_R2_Mean": round(cv_r2_mean, 4),
            "CV_R2_Std": round(cv_r2_std, 4),
            "Test_MAE": round(test_mae, 2),
            "Test_RMSE": round(test_rmse, 2),
            "Test_R2": round(test_r2, 4),
        })

    results_df = pd.DataFrame(results)
    return results_df, trained_models, test_predictions


def plot_actual_vs_predicted(
    y_test: pd.Series,
    test_predictions: Dict[str, np.ndarray],
    output_path: Path
):
    """
    Generates Actual vs. Predicted scatter plots with identity line (y = x).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    models_to_plot = [m for m in test_predictions.keys() if "Baseline" not in m]

    fig, axes = plt.subplots(1, len(models_to_plot), figsize=(6 * len(models_to_plot), 5), sharey=True)
    if len(models_to_plot) == 1:
        axes = [axes]

    # Bound visualization limits for readability
    plot_min, plot_max = -2000, 3000

    for ax, name in zip(axes, models_to_plot):
        y_pred = test_predictions[name]
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        ax.scatter(y_test, y_pred, alpha=0.35, s=20, color="#2563eb", edgecolors="none")
        ax.plot([plot_min, plot_max], [plot_min, plot_max], "r--", linewidth=1.5, label="Ideal Line (y = ŷ)")
        ax.axhline(0, color="gray", linestyle=":", alpha=0.7)
        ax.axvline(0, color="gray", linestyle=":", alpha=0.7)
        ax.set_xlim(plot_min, plot_max)
        ax.set_ylim(plot_min, plot_max)
        ax.set_title(f"{name}\nTest R² = {r2:.3f} | MAE = ${mae:.1f}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Actual Profit ($)")
        if ax == axes[0]:
            ax.set_ylabel("Predicted Profit ($)")
        ax.legend(loc="upper left")
        ax.grid(True, linestyle=":", alpha=0.6)

    plt.suptitle("Held-Out Test Set: Actual vs. Predicted Profit", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_residuals(
    y_test: pd.Series,
    test_predictions: Dict[str, np.ndarray],
    output_path: Path
):
    """
    Generates Residual vs. Predicted and Residual Distribution plots.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best_model_name = "Tree-based (HistGradientBoosting)"
    if best_model_name not in test_predictions:
        best_model_name = list(test_predictions.keys())[-1]

    y_pred = test_predictions[best_model_name]
    residuals = y_test.values - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 1. Residuals vs Predicted
    axes[0].scatter(y_pred, residuals, alpha=0.35, color="#059669", s=20, edgecolors="none")
    axes[0].axhline(0, color="red", linestyle="--", linewidth=1.5)
    axes[0].set_title(f"Residuals vs Predicted ({best_model_name})", fontweight="bold")
    axes[0].set_xlabel("Predicted Profit ($)")
    axes[0].set_ylabel("Residuals ($: Actual - Predicted)")
    axes[0].set_xlim(-1500, 2500)
    axes[0].set_ylim(-3000, 3000)
    axes[0].grid(True, linestyle=":", alpha=0.6)

    # 2. Histogram of residuals
    axes[1].hist(residuals, bins=60, range=(-1500, 1500), color="#10b981", edgecolor="black", alpha=0.7)
    axes[1].axvline(0, color="red", linestyle="--", linewidth=1.5, label="Zero Error")
    axes[1].axvline(np.mean(residuals), color="blue", linestyle="-", label=f"Mean Error: ${np.mean(residuals):.2f}")
    axes[1].set_title("Residual Error Distribution (Trimmed view)", fontweight="bold")
    axes[1].set_xlabel("Residual ($)")
    axes[1].set_ylabel("Count")
    axes[1].legend()
    axes[1].grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def extract_and_plot_feature_importance(
    trained_models: Dict[str, Pipeline],
    output_path: Path
):
    """
    Extracts feature importances from Random Forest and coefficients from Ridge.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rf_pipe = trained_models.get("Tree-based (Random Forest)")
    if rf_pipe is None:
        return

    # Extract feature names from ColumnTransformer
    preprocessor = rf_pipe.named_steps["preprocessor"]
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    cat_feature_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names = NUMERICAL_FEATURES + cat_feature_names

    rf_regressor = rf_pipe.named_steps["regressor"]
    importances = rf_regressor.feature_importances_

    # Create top 15 importance bar plot
    df_imp = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    df_imp = df_imp.sort_values("Importance", ascending=False).head(12)

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(df_imp))
    ax.barh(y_pos, df_imp["Importance"].values, align="center", color="#3b82f6", edgecolor="#1d4ed8")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_imp["Feature"].values)
    ax.invert_yaxis()
    ax.set_xlabel("Relative Gini Feature Importance")
    ax.set_title("Top Predictive Drivers of Order-Level Profit (Random Forest)", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Train Profit Prediction Models")
    parser.add_argument("--input", default="data/cleaned/orders_clean.csv", help="Input cleaned dataset")
    parser.add_argument("--reports", default="reports", help="Directory for reports and tables")
    parser.add_argument("--figures", default="reports/figures", help="Directory for figures")
    parser.add_argument("--models", default="reports/models", help="Directory for saved model binaries")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed")
    args = parser.parse_args()

    input_path = Path(args.input)
    reports_dir = Path(args.reports)
    figures_dir = Path(args.figures)
    models_dir = Path(args.models)

    reports_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset from {input_path}...")
    df = pd.read_csv(input_path)

    print("Splitting data into 80% train and 20% held-out test...")
    X_train, X_test, y_train, y_test = prepare_data(df, test_size=0.20, random_state=args.seed)
    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    models = create_model_pipelines(random_state=args.seed)

    print("\nBeginning 5-fold cross-validation and held-out evaluation...")
    results_df, trained_models, test_predictions = evaluate_models(
        models, X_train, y_train, X_test, y_test, cv_folds=5, random_state=args.seed
    )

    print("\n" + "=" * 80)
    print("MODEL COMPARISON RESULTS")
    print("=" * 80)
    print(results_df.to_string(index=False))

    # Save comparison table
    csv_path = reports_dir / "model_comparison.csv"
    results_df.to_csv(csv_path, index=False)
    json_path = reports_dir / "model_comparison.json"
    results_df.to_json(json_path, orient="records", indent=2)
    print(f"\nSaved model comparison table to {csv_path} and {json_path}")

    # Save experiment config
    config = {
        "target": TARGET_COLUMN,
        "features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
        },
        "excluded_features": LEAKAGE_AND_ID_COLUMNS,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "test_split_ratio": 0.20,
        "cv_folds": 5,
        "random_state": args.seed,
        "metric_definitions": {
            "MAE": "Mean Absolute Error: average magnitude of dollar prediction error.",
            "RMSE": "Root Mean Squared Error: penalized metric emphasizing large loss outliers.",
            "R2": "Coefficient of Determination: fraction of variance explained (can be negative if model is worse than mean)."
        }
    }
    config_path = reports_dir / "experiment_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"Saved experiment config to {config_path}")

    # Generate evaluation plots
    print("Generating evaluation plots...")
    plot_actual_vs_predicted(y_test, test_predictions, figures_dir / "actual_vs_predicted.png")
    plot_residuals(y_test, test_predictions, figures_dir / "residuals_analysis.png")
    extract_and_plot_feature_importance(trained_models, figures_dir / "feature_importance.png")
    print(f"Plots saved to {figures_dir}")

    # Serialize best performing model
    best_model_name = "Tree-based (HistGradientBoosting)"
    best_pipeline = trained_models[best_model_name]
    model_save_path = models_dir / "best_profit_model.joblib"
    joblib.dump(best_pipeline, model_save_path)
    print(f"Serialized best model ({best_model_name}) to {model_save_path}")

    print("\nMachine Learning Experiment completed successfully.")


if __name__ == "__main__":
    main()
