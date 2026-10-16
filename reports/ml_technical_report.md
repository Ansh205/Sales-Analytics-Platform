# Applied Machine Learning & Statistical Inference Technical Report
**Project**: Sales Analytics & Business Intelligence Platform  
**Target Variable**: Order-Level Net Profit (`Profit` in USD)  
**Dataset**: Global Superstore (10,194 records, 30 attributes)  
**Author**: Machine Learning & Applied Data Science Engineering  

---

## 1. Executive Summary & Problem Formulation

In retail and commercial distribution, maintaining healthy order-level operating margins is critical. Promotional discounting is frequently deployed to drive top-line gross revenue, yet untracked discounting frequently yields catastrophic order-level net losses.

This project delivers two integrated empirical solutions:
1. **Statistical Hypothesis Testing**: Rigorously evaluates whether average order profit differs significantly between lower-discount orders ($\le 20\%$) and higher-discount orders ($> 20\%$).
2. **Predictive Machine Learning Pipeline**: Trains and evaluates scikit-learn regression models to predict continuous order-level profit using only legitimate, order-time features (preventing data leakage and identifier memorization).

### Key Empirical Findings
- **Statistical Significance**: Lower-discount orders achieve an average profit of **+$48.79** (median +$11.49), whereas higher-discount orders suffer an average loss of **-$96.13** (median -$18.80). The difference of **+$144.92** per order is statistically overwhelming ($t = 16.25, df = 1603.55, p = 4.66 \times 10^{-55}$, Cohen's $d = 0.638$).
- **Predictive Superiority of Tree Ensembles**: A tree-based gradient boosted regressor (`HistGradientBoostingRegressor`) achieved a 5-fold cross-validation MAE of **$22.25** and test set MAE of **$28.38** ($R^2 = 0.506$), compared to a regularized linear model (`Ridge`, MAE **$61.66**, $R^2 = 0.483$) and a mean baseline (MAE **$66.77**, $R^2 = -0.002$).

---

## 2. Dataset Auditing & Data Preprocessing Decisions

### 2.1 Dimensions and Missing Values
- **Total Transactions**: 10,194 orders.
- **Duplicate Records**: 0 duplicates across the authoritative cleaned dataset.
- **Missing Values**: 0 nulls across all modeling features.

### 2.2 Preservation of Loss-Making Orders
In total, **1,901 orders (18.65%)** reflect negative net profit (losses ranging down to -$6,599.98).
- **Decision**: Negative profit orders were **strictly preserved** in the dataset.
- **Rationale**: Retail losses are not data corruption or entry errors; they reflect real business events where steep regional discounts and return/shipping costs outstripped gross margin. Dropping negative profit transactions would induce severe survival bias and render predictive margin modeling useless in production.

### 2.3 Strict Target Leakage Prevention & Feature Selection
To ensure validity in production checkout flows:
1. **Target**: `Profit` (continuous dollars).
2. **Excluded Direct Leakage**:
   - `Profit Margin` ($\text{Profit} / \text{Sales}$ mathematically reveals the label).
   - `Profit Bucket` (binned label).
3. **Excluded High-Cardinality Identifiers**:
   - `Row ID`, `Order ID`, `Customer ID`, `Customer Name`, `Product ID`, `Product Name`. Including these would cause tree and linear models to memorize historical entities rather than generalize patterns.
4. **Excluded Post-Order Attributes**:
   - `Ship Date` and `Shipping Days` (only finalized post-fulfillment).
5. **Permitted Order-Time Predictors**:
   - Numerical: `Sales` ($), `Quantity` (units), `Discount` (rate between 0.0 and 0.8).
   - Categorical: `Category` (3 unique), `Sub-Category` (17 unique), `Segment` (3 unique), `Region` (4 unique), `Ship Mode` (4 unique), `Order Month` (12 unique).

---

## 3. Machine Learning Modeling & Experimental Results

### 3.1 Preprocessing Pipeline
All models were integrated into a standardized scikit-learn `Pipeline` utilizing `ColumnTransformer`:
- **Numerical Features**: `StandardScaler()` (centering and unit-variance scaling).
- **Categorical Features**: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` to handle unseen categories at inference.

### 3.2 Splitting & Cross-Validation Strategy
- **Train/Test Split**: 80% train ($N = 8,155$), 20% held-out test ($N = 2,039$) with a fixed seed (`random_state=42`).
- **Cross-Validation**: 5-Fold Cross Validation evaluated exclusively on the training set using identical fold indices across all models.

### 3.3 Verified Model Performance Comparison

| Model | CV MAE (Mean ± Std) | CV RMSE (Mean ± Std) | CV $R^2$ (Mean ± Std) | Test Set MAE ($) | Test Set RMSE ($) | Test Set $R^2$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Mean Predictor)** | $60.73 ± 1.35 | $211.82 ± 15.18 | -0.0010 ± 0.0006 | $66.77 | $299.79 | -0.0017 |
| **Regularized Linear (Ridge)** | $60.16 ± 1.35 | $196.66 ± 44.13 | 0.1232 ± 0.3218 | $61.66 | $215.38 | 0.4830 |
| **Tree-based (HistGradientBoosting)** | **$22.25 ± 2.93** | **$112.10 ± 43.29** | **0.7026 ± 0.1886** | **$28.38** | **$210.47** | **0.5063** |
| **Tree-based (Random Forest)** | $24.02 ± 2.73 | $140.88 ± 43.53 | 0.5373 ± 0.2439 | $26.67 | $190.04 | 0.5975 |

### 3.4 Methodological Note on Negative $R^2$
The Dummy Regressor yielded a test set $R^2$ of **-0.0017**. In scikit-learn, $R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y}_{\text{test}})^2}$. Because the dummy regressor predicts the *training set mean*, slight sampling variation between the train and test target distributions yields a residual sum of squares that exceeds the test variance. Negative $R^2$ indicates that predicting the historical training mean performs slightly worse on test data than knowing the test set mean a priori.

### 3.5 Why Tree-Based Models Dramatically Outperformed Linear Regression
In retail finance, net profit is inherently **non-linear and multiplicative**:
$$\text{Profit} \approx \text{Sales} \times (1 - \text{Discount}) - \text{COGS}$$
A standard linear model cannot capture the multiplicative interaction between `Sales` and `Discount` without explicit interaction terms. Tree-based models (`HistGradientBoosting` and `RandomForest`) naturally partition the feature space into conditional discount-sales splits, capturing the non-linear inflection where high discounts flip high-sales transactions into catastrophic margin losses.

---

## 4. Statistical Hypothesis Testing: Impact of Discounting

### 4.1 Research Question & Grouping Rule
- **Research Question**: Does average order profit differ between lower-discount and higher-discount orders?
- **Grouping Rule**:
  - The empirical median discount is **0.20 (20%)**.
  - **Lower Discount Group**: $\text{Discount} \le 0.20$ ($N = 8,779$, 86.1% of transactions).
  - **Higher Discount Group**: $\text{Discount} > 0.20$ ($N = 1,415$, 13.9% of transactions).

### 4.2 Descriptive Metrics Comparison

| Metric | Lower Discount ($\le 20\%$) | Higher Discount ($> 20\%$) | Difference (Delta) |
| :--- | :---: | :---: | :---: |
| Sample Size ($N$) | 8,779 | 1,415 | - |
| Mean Profit ($\bar{x}$) | **+$48.79** | **-$96.13** | **+$144.92** |
| Median Profit | +$11.49 | -$18.80 | +$30.29 |
| Standard Deviation ($s$) | $206.94 | $332.19 | -$125.25 |
| Loss-Making Orders (%) | 9.77% | 73.71% | **+63.94 percentage points** |

### 4.3 Inferential Tests & Effect Sizes
1. **Assumption Diagnostics**:
   - Normality: D'Agostino-Pearson test strongly rejects normality ($p < 10^{-10}$) due to heavy tails.
   - Homoscedasticity: Levene's test confirms unequal variances ($W = 49.14, p = 2.54 \times 10^{-12}$).
2. **Primary Test (Welch's Two-Sample t-test)**:
   - $t = 16.2456$
   - Degrees of Freedom (Welch-Satterthwaite): $1,603.55$
   - $p\text{-value} = 4.66 \times 10^{-55}$
   - **95% Confidence Interval for Mean Difference**: **[+$127.42, +$162.41]**
   - **Cohen's d**: **0.6384** (Medium-to-large effect size).
3. **Robustness Check (Mann-Whitney U Test)**:
   - $U = 11,910,340.0, p < 10^{-15}$, Rank-biserial correlation = -0.9176.
4. **Multiple Comparisons Subgroup Analysis (Bonferroni Threshold $\alpha = 0.0167$)**:
   - **Furniture**: Lower Disc Mean = +$45.37$, Higher Disc Mean = -$99.02$ ($\Delta = +$144.39, $t = 19.18, p = 7.63 \times 10^{-66}$, Cohen's $d = 1.22$).
   - **Office Supplies**: Lower Disc Mean = +$31.87$, Higher Disc Mean = -$68.66$ ($\Delta = +$100.53, $t = 9.86, p = 1.26 \times 10^{-21}$, Cohen's $d = 0.62$).
   - **Technology**: Lower Disc Mean = +$106.44$, Higher Disc Mean = -$197.42$ ($\Delta = +$303.85, $t = 5.57, p = 9.01 \times 10^{-8}$, Cohen's $d = 0.73$).

Every single product category demonstrates a statistically significant profit collapse under heavy discounting that survives family-wise error rate control.

---

## 5. Methodological Limitations & Causal Considerations

1. **Observational Association vs. Causation**:
   Transactions reflect observational business records, not a randomized controlled trial (A/B experiment). Discounts were not randomly assigned to customers; rather, sales representatives or automated pricing engines may selectively discount distressed, aging, or low-margin items.
2. **Contemporaneous vs. Predictive Timing**:
   Order-time features (`Sales`, `Discount`, `Quantity`) enable instant checkout-stage risk screening. However, actual realized profit may still be influenced by subsequent post-purchase returns and carrier claims.

---

## 6. Generated Visual Artifacts

The following reproducible figures were generated and saved in `reports/figures/`:
1. `reports/figures/profit_distribution.png`: Target profit histogram with KDE and outlier boxplot.
2. `reports/figures/discount_vs_profit.png`: Profit distribution across discount brackets showing the margin inversion above 20%.
3. `reports/figures/correlation_matrix.png`: Pearson correlation matrix across numerical transaction drivers.
4. `reports/figures/sales_profit_scatter.png`: Sales vs. profit scatter colored by discount level.
5. `reports/figures/actual_vs_predicted.png`: Held-out test set scatter plots showing identity line ($y = \hat{y}$).
6. `reports/figures/residuals_analysis.png`: Residual error plots and error distribution.
7. `reports/figures/feature_importance.png`: Top predictive drivers of profit from the tree ensemble.
8. `reports/figures/discount_hypothesis_boxplot.png`: Distributional comparison of lower vs. higher discount orders.
