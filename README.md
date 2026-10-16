# Sales Analytics & Machine Learning Platform

An end-to-end Enterprise Business Intelligence, Statistical Inference, and Applied Machine Learning platform built with **Python**, **scikit-learn**, **SciPy**, **PostgreSQL**, **FastAPI**, and **Power BI**.

The platform couples a full ETL & SQL data warehousing pipeline on the Global Superstore dataset with rigorous data quality profiling, observational hypothesis testing on promotional discounting, and order-level profit prediction using leak-free scikit-learn pipelines.

---

## Architecture Overview

```text
Global Superstore (Raw Excel / Cleaned CSV)
                 ↓
     ETL & Quality Profiling (scripts/etl & scripts/ml/data_profiling.py)
                 ↓
   PostgreSQL Warehouse (Relational Schema & Optimized Views)
      ↙                         ↓                                 ↘
Power BI Dashboards      FastAPI REST Layer              Applied ML & Inference
(Executive/Sales)      (/api/summary, /api/ml/*)         (scikit-learn / SciPy)
```

---

## Core Capabilities & Features

### 1. Automated ETL & Warehouse Pipeline
- Automated extraction, validation, cleaning, and feature engineering across 10,194 transaction records.
- PostgreSQL database integration with connection pooling, indexes, and reporting views (`vw_executive_summary`, `vw_sales_summary`, `vw_profit_summary`).

### 2. Rigorous Data Quality & Profiling (`scripts/ml/data_profiling.py`)
- Full data integrity verification (negative sales, zero sales, discount boundary checks).
- Detection and characterization of **1,901 loss-making orders (18.65%)**; documented decision to preserve negative profit rows to prevent survival bias.
- Skewness, kurtosis, and IQR outlier detection across financial metrics.
- Automated publication of `reports/data_quality_report.md` and distribution figures.

### 3. Statistical Hypothesis Testing on Promotional Discounting (`scripts/ml/statistical_analysis.py`)
- **Analytical Question**: *Does average order profit differ between lower-discount orders ($\le 20\%$) and higher-discount orders ($> 20\%$)?*
- **Empirical Grouping**: Median split at 20% discount (separating standard allowances from steep clearance markdowns).
- **Diagnostics**: D'Agostino-Pearson normality tests and Levene's test for heteroscedasticity.
- **Inferential Tests**: **Welch's Two-Sample t-test** (robust to unequal variances) and non-parametric **Mann-Whitney U test**.
- **Subgroup Analysis**: Segmented evaluation across merchandise categories with **Bonferroni correction** ($\alpha_{\text{adj}} = 0.0167$).
- **Methodological Guardrails**: Explicit documentation establishing that observational association does not equal causation.

### 4. Order-Level Profit Prediction Machine Learning (`scripts/ml/train_profit_model.py`)
- **Target Variable**: Continuous net order profit (`Profit` in USD).
- **Leakage Prevention**: Excluded `Profit Margin`, `Profit Bucket`, post-order shipping metrics (`Shipping Days`), and high-cardinality identifiers (`Order ID`, `Customer Name`, `Product ID`) to prevent memorization.
- **Preprocessing**: scikit-learn `Pipeline` and `ColumnTransformer` (`StandardScaler` on numerical features, `OneHotEncoder(handle_unknown='ignore')` on categorical features).
- **Cross-Validation**: 5-Fold Cross-Validation on the 80% training set ($N = 8,155$) and evaluation on 20% held-out test set ($N = 2,039$).
- **Models Compared**:
  1. Baseline Mean Predictor (`DummyRegressor`)
  2. Regularized Linear Regression (`Ridge`, $\alpha=10.0$)
  3. Tree-based Gradient Boosting (`HistGradientBoostingRegressor`)
  4. Tree-based Ensemble (`RandomForestRegressor`)

### 5. Production API Integration (`app/routes/ml.py`)
- `GET /api/ml/summary`: Exposes precomputed model comparison metrics, cross-validation scores, experiment parameters, and hypothesis test results without retraining models on request.
- `POST /api/ml/predict`: Real-time order profit scoring and margin risk classification (`HEALTHY_MARGIN`, `MODERATE_MARGIN`, `HIGH_MARGIN_RISK`) using the serialized model singleton.

---

## Empirical Results & Verified Metrics

### 1. Machine Learning Model Performance

| Model Architecture | 5-Fold CV MAE ($) | 5-Fold CV RMSE ($) | 5-Fold CV $R^2$ | Test Set MAE ($) | Test Set RMSE ($) | Test Set $R^2$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Mean Predictor)** | $60.73 ± 1.35 | $211.82 ± 15.18 | -0.0010 ± 0.0006 | $66.77 | $299.79 | -0.0017 |
| **Regularized Linear (Ridge)** | $60.16 ± 1.35 | $196.66 ± 44.13 | 0.1232 ± 0.3218 | $61.66 | $215.38 | 0.4830 |
| **Tree-based (HistGradientBoosting)** | **$22.25 ± 2.93** | **$112.10 ± 43.29** | **0.7026 ± 0.1886** | **$28.38** | **$210.47** | **0.5063** |
| **Tree-based (Random Forest)** | $24.02 ± 2.73 | $140.88 ± 43.53 | 0.5373 ± 0.2439 | $26.67 | $190.04 | 0.5975 |

> **Why Negative $R^2$ Occurs**: The Baseline model predicts the training set mean. On the held-out test set, slight divergence between train and test target means causes the residual sum of squares to exceed the total sum of squares ($R^2 = 1 - SS_{\text{res}} / SS_{\text{tot}} < 0$). This is mathematically expected for a mean baseline and is not concealed.

### 2. Statistical Hypothesis Test Results

- **Sample Sizes**:
  - Lower Discount ($\le 20\%$): $N = 8,779$ (86.1% of transactions)
  - Higher Discount ($> 20\%$): $N = 1,415$ (13.9% of transactions)
- **Descriptive Comparison**:
  - Lower Discount Group: Mean = **+$48.79**, Median = **+$11.49**, Loss Orders = **9.77%**
  - Higher Discount Group: Mean = **-$96.13**, Median = **-$18.80**, Loss Orders = **73.71%**
- **Test Statistics**:
  - **Mean Difference**: **+$144.92** per order
  - **95% Confidence Interval**: **[+$127.42, +$162.41]**
  - **Welch's t-statistic**: `16.2456` ($df = 1,603.55$)
  - **p-value**: `4.66e-55` ($p \ll 0.0001$)
  - **Effect Size (Cohen's d)**: `0.6384` (Medium-to-large standardized effect)
  - **Mann-Whitney U**: `11,910,340.0` ($p < 10^{-15}$)
- **Statistical Decision**: **Reject Null Hypothesis ($H_0$)**. Steep promotional discounting significantly degrades order-level profitability across all tested merchandise categories.

---

## Reproducing Experiments & Running Tests

### 1. Environment Setup
```powershell
# Activate existing virtual environment
.\venv\Scripts\Activate.ps1

# Install / verify required dependencies
pip install -r requirements.txt
```

### 2. Run Data Profiling & Generate Quality Report
```powershell
python scripts/ml/data_profiling.py --input data/cleaned/orders_clean.csv --output reports/data_quality_report.md --figures reports/figures
```

### 3. Run Machine Learning Training & Evaluation
```powershell
python scripts/ml/train_profit_model.py --input data/cleaned/orders_clean.csv --reports reports --figures reports/figures --models reports/models --seed 42
```

### 4. Run Statistical Hypothesis Testing
```powershell
python scripts/ml/statistical_analysis.py --input data/cleaned/orders_clean.csv --reports reports --figures reports/figures --threshold 0.20
```

### 5. Execute Comprehensive Test Suite
```powershell
# Run with Python standard unittest runner (37 tests)
python -m unittest discover tests

# Or run with pytest (38 tests)
pytest -v
```

### 6. Launch FastAPI Application
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Analytics UI Dashboard: `http://127.0.0.1:8000/dashboard`
- ML Experiment Summary: `http://127.0.0.1:8000/api/ml/summary`

---

## Directory Structure

```text
├── app/
│   ├── database.py                 # PostgreSQL SQLAlchemy connection & session pooling
│   ├── main.py                     # FastAPI application & template mounts
│   └── routes/
│       ├── analytics.py            # Business KPI endpoints & parameterized SQL views
│       └── ml.py                   # ML summary & real-time order profit scoring
├── data/
│   ├── raw/Global_Superstore.xls   # Raw original Excel dataset
│   └── cleaned/orders_clean.csv    # Authoritative cleaned dataset (10,194 rows)
├── reports/
│   ├── data_quality_report.md      # Automated data quality & profiling report
│   ├── data_quality_metrics.json   # Machine-readable profiling metrics
│   ├── experiment_config.json      # ML experiment parameters & random seeds
│   ├── model_comparison.csv        # Tabular model evaluation metrics
│   ├── model_comparison.json       # JSON model comparison metrics
│   ├── ml_technical_report.md      # Academic-grade technical report
│   ├── statistical_hypothesis_report.md
│   ├── statistical_hypothesis_results.json
│   ├── figures/                    # Generated visualization artifacts
│   │   ├── actual_vs_predicted.png
│   │   ├── correlation_matrix.png
│   │   ├── discount_hypothesis_boxplot.png
│   │   ├── discount_vs_profit.png
│   │   ├── feature_importance.png
│   │   ├── profit_distribution.png
│   │   ├── residuals_analysis.png
│   │   └── sales_profit_scatter.png
│   └── models/
│       └── best_profit_model.joblib # Serialized HistGradientBoosting pipeline
├── scripts/
│   ├── etl/                        # Core ETL modules (extract, clean, validate)
│   ├── database/                   # Schema generation and warehouse loaders
│   └── ml/
│       ├── data_profiling.py       # Quality auditing, outlier & skewness analysis
│       ├── train_profit_model.py   # Leak-free scikit-learn training & CV evaluation
│       └── statistical_analysis.py # Welch's t-test, Mann-Whitney U, Bonferroni
├── sql/                            # Table schemas, index definitions, and views
├── templates/                      # Jinja2 frontend analytical dashboards
└── tests/
    ├── test_analytics.py           # Core analytics API tests
    ├── test_database.py            # PostgreSQL connection & integrity tests
    ├── test_ml.py                  # ML pipeline, leakage prevention, & endpoint tests
    └── test_statistics.py          # Welch t-test, descriptives, & Bonferroni tests
```

---

## Suggested Resume / Portfolio Bullets

- **Engineered an End-to-End Sales Analytics & ML Platform** integrating Python, PostgreSQL, and FastAPI with a scikit-learn predictive modeling pipeline over 10K+ Global Superstore transactions.
- **Architected Leak-Free Feature Pipelines** using `ColumnTransformer` and `StandardScaler`/`OneHotEncoder`, eliminating 11 direct label and post-fulfillment leaks to predict order-level profit.
- **Benchmarked Regression Ensembles** across 5-fold cross-validation; gradient boosting (`HistGradientBoostingRegressor`) surpassed baseline and regularized linear regression by 63% (reducing CV MAE from $60.73 to $22.25, test $R^2 = 0.506$).
- **Conducted Inferential Hypothesis Testing** with Welch's t-test and Mann-Whitney U tests ($t = 16.25, p < 10^{-50}$, Cohen's $d = 0.638$), demonstrating that promotional discounts $>20\%$ inverted mean order profitability from +$48.79 to -$96.13 across all categories under Bonferroni correction.
- **Deployed Production REST Endpoints** in FastAPI for real-time order margin risk classification and experiment summaries using serialized model singletons without request-time retraining.
- **Authored Rigorous Test Suite & Technical Artifacts** with 38 unit and integration tests (100% pass rate in pytest) covering edge cases, numerical cancellations, and pipeline transformations.
