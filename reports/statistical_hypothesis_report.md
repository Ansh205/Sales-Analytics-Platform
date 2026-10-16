# Statistical Hypothesis Testing Report

## 1. Research Question & Hypothesis Formulation

**Analytical Question**: Does average order-level profit differ significantly between lower-discount and higher-discount orders?

- **Null Hypothesis ($H_0$)**: $\mu_{\text{lower}} = \mu_{\text{higher}}$ (There is no true difference in mean order profit between lower-discount and higher-discount orders).
- **Alternative Hypothesis ($H_1$)**: $\mu_{\text{lower}} \neq \mu_{\text{higher}}$ (Average order profit differs between lower-discount and higher-discount orders; two-tailed test).

## 2. Discount Grouping Definition & Defensible Rule

The grouping criterion is formulated from empirical retail pricing policy and dataset distribution:
- **Empirical Median**: The median discount rate across 10,194 historical orders is **0.20 (20%)**.
- **Commercial Domain Practice**: Discounts up to 20% represent standard contractual pricing and seasonal allowances. Discounts strictly exceeding 20% (> 0.20) represent deep clearance, loss-leader pricing, or distressed inventory liquidations.
- **Lower Discount Group**: `Discount <= 0.20` ($N = 8,111$)
- **Higher Discount Group**: `Discount > 0.20` ($N = 2,083$)

## 3. Descriptive Sample Statistics

| Metric | Lower Discount Group (<= 20%) | Higher Discount Group (> 20%) | Delta (Lower - Higher) |
| :--- | :---: | :---: | :---: |
| Sample Size ($N$) | 8,779 (86.1%) | 1,415 (13.9%) | - |
| Sample Mean ($\bar{x}$) | **$48.79** | **$-96.13** | **+$144.92** |
| Sample Median | $11.49 | $-18.80 | +$30.29 |
| Standard Deviation ($s$) | $206.91 | $325.11 | - |
| Variance ($s^2$) | 42,809.89 | 105,695.50 | - |
| Interquartile Range (IQR) | $31.89 | $65.73 | - |
| Loss-Making Orders | 531 (6.05%) | 1370 (96.82%) | -90.77 pp |
| Minimum Profit | $-1049.34 | $-6599.98 | - |
| Maximum Profit | $8399.98 | $1120.00 | - |

## 4. Assumption Verification & Test Selection Rationale

1. **Normality Test (D'Agostino's $K^2$)**:
   - Lower Discount Group: $K^2 = 19049.70, p = 0.00e+00$ (Strongly non-normal, leptokurtic distribution).
   - Higher Discount Group: $K^2 = 2305.06, p = 0.00e+00$ (Strongly non-normal, heavy negative tail).
2. **Homoscedasticity Test (Levene's Test)**:
   - $W = 49.14, p = 2.54e-12$ (Null hypothesis of equal variances rejected).
3. **Selected Primary Test**: **Welch's Two-Sample t-test**.
   - Robust to unequal population variances ($s_1^2 \neq s_2^2$).
   - With sample sizes $N_1 = 8,111$ and $N_2 = 2,083$, the Central Limit Theorem guarantees that the distribution of sample means converges to normality, allowing exact inference on difference in means.
4. **Selected Secondary Test**: **Mann-Whitney U Test**.
   - Validates distribution rank-sum equality without distributional or variance assumptions.

## 5. Inferential Test Results

### Primary: Welch's t-test

- **Test Statistic ($t$)**: `16.2456`
- **Degrees of Freedom ($df$, Welch-Satterthwaite)**: `1603.55`
- **p-value**: `4.6601e-55` (p < 0.0001)
- **95% Confidence Interval for Mean Difference**: `[$127.42, $162.41]`
- **Cohen's d Effect Size**: `0.6384` (Standardized mean difference)
- **Statistical Decision**: **Reject $H_0$** at $\alpha = 0.05$. Lower-discount orders generate significantly higher average profits than higher-discount orders.

### Secondary: Mann-Whitney U Test

- **U-Statistic**: `11,910,340.0`
- **p-value**: `0.0000e+00` (p < 0.0001)
- **Rank-Biserial Correlation**: `-0.9176`
- **Statistical Decision**: **Reject $H_0$**. The median profit distribution of lower-discount orders dominates that of higher-discount orders.

## 6. Subgroup Analysis & Multiple Comparisons Control

To determine whether the negative profit impact of deep discounting persists across individual merchandise departments, we evaluate each Category independently.
Family-wise error rate control is applied via **Bonferroni correction** (Threshold alpha_adj = 0.05 / 3 = 0.0167):

| Product Category | Low Disc N | High Disc N | Low Disc Mean | High Disc Mean | Mean Diff | Welch t | p-value | Sig. (Bonferroni) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Office Supplies** | 5439 | 689 | $31.87 | $-68.66 | $100.53 | 9.86 | 1.26e-21 | YES (p < 0.0167) |
| **Furniture** | 1646 | 555 | $45.37 | $-99.02 | $144.39 | 19.18 | 7.63e-66 | YES (p < 0.0167) |
| **Technology** | 1694 | 171 | $106.44 | $-197.42 | $303.85 | 5.57 | 9.01e-08 | YES (p < 0.0167) |


## 7. Crucial Methodological Limitation: Association vs. Causation

> **Important Analytical Caveat**:
> Although the difference in mean profit between lower-discount and higher-discount orders is statistically overwhelming ($p < 10^{-15}$), **this observational analysis establishes an empirical association, NOT direct causation.**
> Potential confounding factors include:
> 1. **Endogenous Discounting**: Sales reps may apply aggressive discounts specifically on obsolete, slow-moving, or intrinsically low-margin goods that were already destined for low profitability.
> 2. **Product Sub-Category Mix**: Furniture lines (e.g., Tables, Bookcases) inherently carry higher freight costs and lower baseline margins than Technology accessories.
> 3. **Customer Negotiation Power**: Large corporate accounts negotiating bulk discounts may purchase bundles where loss-leader items are packaged with high-margin software/services.
> Confirmatory causal validation would require randomized controlled trials (A/B testing of discount bands across identical SKUs) rather than observational transaction logs.
