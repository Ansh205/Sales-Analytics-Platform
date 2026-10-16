# Data Quality, Preprocessing & Exploratory Profiling Report

## 1. Executive Summary & Dataset Dimensions

- **Total Records (Rows)**: 10,194
- **Total Attributes (Columns)**: 30
- **Duplicate Rows**: 0
- **Numerical Attributes**: 10
- **Categorical Attributes**: 20
- **Datetime Attributes**: 0

## 2. Data Integrity & Domain Business Rule Audits

| Integrity Check | Observed Value | Expected Domain Rule | Status |
| :--- | :---: | :---: | :---: |
| Negative Sales | 0 | 0 (Sales >= 0) | PASS |
| Invalid Quantities (<=0) | 0 | 0 (Quantity >= 1) | PASS |
| Discount Out of [0, 1] Range | 0 | 0 (0 <= Discount <= 1.0) | PASS |
| Loss-Making Orders (Profit < 0) | 1901 (18.65%) | Business reality (heavy discounting) | EXPECTED |
| Profitable Orders (Profit > 0) | 8228 | Normal retail operations | EXPECTED |
| Break-Even Orders (Profit = 0) | 65 | Zero profit margin | EXPECTED |

> **Important Preprocessing Decision Note on Loss-Making Orders:**
> Negative profit values represent genuine retail losses primarily induced by aggressive regional discounting.
> **They are NOT data corruption or entry errors and MUST NOT be dropped or imputed.**
> Deleting negative profit transactions would induce survival bias and invalidate predictive modeling.

## 3. Missing Value & Nullness Analysis

No missing or null values were identified across the cleaned analytical dataset.

## 4. Numerical Distributions, Skewness & Outlier Analysis

| Feature | Mean | Median (Q50) | Std Dev | Min | Max | Skewness | Kurtosis | Outliers (IQR) | Outlier % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Row ID** | 5097.50 | 5097.50 | 2942.90 | 1.00 | 10194.00 | 0.00 | -1.20 | 0 | 0.00% |
| **Sales** | 228.23 | 53.91 | 619.91 | 0.44 | 22638.48 | 12.98 | 306.37 | 1183 | 11.60% |
| **Quantity** | 3.79 | 3.00 | 2.23 | 1.00 | 14.00 | 1.27 | 1.96 | 175 | 1.72% |
| **Discount** | 0.16 | 0.20 | 0.21 | 0.00 | 0.80 | 1.69 | 2.42 | 874 | 8.57% |
| **Profit** | 28.67 | 8.69 | 232.47 | -6599.98 | 8399.98 | 7.60 | 401.69 | 1913 | 18.77% |
| **Order Year** | 2021.72 | 2022.00 | 1.13 | 2020.00 | 2023.00 | -0.28 | -1.31 | 0 | 0.00% |
| **Order Quarter** | 2.88 | 3.00 | 1.06 | 1.00 | 4.00 | -0.46 | -1.06 | 0 | 0.00% |
| **Order Week** | 32.10 | 35.00 | 14.32 | 1.00 | 53.00 | -0.42 | -1.00 | 0 | 0.00% |
| **Shipping Days** | 3.96 | 4.00 | 1.74 | 0.00 | 11.00 | -0.41 | -0.23 | 2 | 0.02% |
| **Profit Margin** | 0.12 | 0.27 | 0.46 | -2.75 | 0.50 | -2.90 | 10.22 | 971 | 9.53% |


### Distribution Findings & Outlier Treatment Rationale

- **Profit Target Distribution**: Highly leptokurtic and skewed (positive and negative extremes). Minimum is -$6,599.98 and maximum is $8,399.98. Tree-based regressors with Huber or absolute error loss are robust to these heavy tails without arbitrary record truncation.
- **Sales Outliers**: Large commercial orders (e.g. Cisco telepresence systems, Canon copiers) generate high revenue outliers. These represent authentic transactions in the B2B customer segment.

## 5. Feature Relationships & Target Correlations (Profit)

| Numerical Feature | Pearson Correlation (Linear) | Spearman Correlation (Monotonic Rank) | Business Interpretation |
| :--- | :---: | :---: | :--- |
| Row ID | +0.0030 | -0.0003 | Auxiliary calendar / engineered metric. |
| Sales | +0.4815 | +0.5204 | Moderate positive association; higher sales often yield higher gross profit, modulated by margin. |
| Quantity | +0.0661 | +0.2354 | Weak correlation; volume alone does not guarantee profit without considering unit margin and discount. |
| Discount | -0.2189 | -0.5415 | Negative correlation; higher discount rates directly erode margin and trigger steep order losses. |
| Order Year | +0.0046 | -0.0037 | Auxiliary calendar / engineered metric. |
| Order Quarter | -0.0028 | +0.0058 | Auxiliary calendar / engineered metric. |
| Order Week | -0.0046 | +0.0082 | Auxiliary calendar / engineered metric. |
| Shipping Days | -0.0043 | -0.0057 | Negligible linear relationship with profit margin. |
| Profit Margin | +0.2232 | +0.4960 | Auxiliary calendar / engineered metric. |


## 6. Categorical Cardinality & Feature Structure

| Categorical Feature | Cardinality (Unique) | Top Category | Top Frequency | Top % | Preprocessing Strategy |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Order ID | 5111 | Us-2023-100111 | 14 | 0.1% | Exclude from ML features to prevent high-cardinality memorization & leakage |
| Order Date | 1242 | 2022-09-05 | 38 | 0.4% | Standard categorical encoding |
| Ship Date | 1338 | 2021-12-16 | 38 | 0.4% | Standard categorical encoding |
| Ship Mode | 4 | Standard Class | 6120 | 60.0% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| Customer ID | 804 | Wb-21850 | 41 | 0.4% | Exclude from ML features to prevent high-cardinality memorization & leakage |
| Customer Name | 800 | William Brown | 41 | 0.4% | Exclude from ML features to prevent high-cardinality memorization & leakage |
| Segment | 3 | Consumer | 5281 | 51.8% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| Country/Region | 2 | United States | 9994 | 98.0% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| City | 542 | New York City | 915 | 9.0% | Standard categorical encoding |
| State/Province | 59 | California | 2001 | 19.6% | Standard categorical encoding |
| Postal Code | 654 | 10035 | 263 | 2.6% | Standard categorical encoding |
| Region | 4 | West | 3253 | 31.9% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| Product ID | 1862 | Fur-Fu-10004270 | 20 | 0.2% | Exclude from ML features to prevent high-cardinality memorization & leakage |
| Category | 3 | Office Supplies | 6128 | 60.1% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| Sub-Category | 17 | Binders | 1548 | 15.2% | One-Hot Encoding or Frequency/Target Encoding |
| Product Name | 1849 | Staples | 50 | 0.5% | Exclude from ML features to prevent high-cardinality memorization & leakage |
| Order Month | 12 | November | 1474 | 14.5% | One-Hot Encoding or Frequency/Target Encoding |
| Order Day | 7 | Monday | 1867 | 18.3% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| Sales Bucket | 4 | Low | 6378 | 62.6% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |
| Profit Bucket | 3 | Low Profit | 7387 | 72.5% | One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) |


## 7. Data Leakage & Feature Selection Directives

For predictive modeling (Target: `Profit`), the following features are strictly categorized:

1. **Target Feature**: `Profit` (Excluded from training inputs).
2. **Target Leakage Features (Must be Excluded)**:
   - `Profit Margin` (`Profit / Sales` mathematically leaks the target directly).
   - `Profit Bucket` (Derived directly from profit thresholds).
3. **Post-Fulfillment Features (Excluded for At-Order Inference)**:
   - `Ship Date`, `Shipping Days` (Only finalized when package leaves warehouse).
4. **High-Cardinality Identifiers (Excluded to Prevent Memorization)**:
   - `Row ID`, `Order ID`, `Customer ID`, `Customer Name`, `Product ID`, `Product Name`.
5. **Legitimate Order-Time Predictors (Permitted Inputs)**:
   - `Sales`, `Quantity`, `Discount`, `Category`, `Sub-Category`, `Segment`, `Region`, `Ship Mode`, `Order Month`, `Order Day`.

## 8. Visual Evidence Artifacts

- `reports/figures/profit_distribution.png`
- `reports/figures/discount_vs_profit.png`
- `reports/figures/correlation_matrix.png`
- `reports/figures/sales_profit_scatter.png`

