"""
data_profiling.py

Comprehensive Data Quality and Statistical Profiling Module.
Inspects shape, types, missing values, duplicates, distributions, outliers,
categorical cardinality, and correlations with business target (Profit).
Generates reproducible Markdown reports and publication-grade figures.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def compute_numerical_profile(df: pd.DataFrame, num_cols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Computes summary statistics, skewness, kurtosis, and IQR-based outlier metrics
    for numerical columns.
    """
    profile = {}
    for col in num_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        q25 = float(series.quantile(0.25))
        q50 = float(series.quantile(0.50))
        q75 = float(series.quantile(0.75))
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outliers = series[(series < lower_bound) | (series > upper_bound)]

        profile[col] = {
            "count": int(series.count()),
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "q25": q25,
            "median": q50,
            "q75": q75,
            "max": float(series.max()),
            "skewness": float(series.skew()),
            "kurtosis": float(series.kurtosis()),
            "iqr_lower_bound": float(lower_bound),
            "iqr_upper_bound": float(upper_bound),
            "outlier_count": int(outliers.count()),
            "outlier_percentage": float((outliers.count() / len(series)) * 100.0),
        }
    return profile


def compute_categorical_profile(df: pd.DataFrame, cat_cols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Computes unique counts, top frequency, and cardinality for categorical columns.
    """
    profile = {}
    for col in cat_cols:
        series = df[col].astype(str)
        val_counts = series.value_counts()
        top_val = val_counts.index[0] if not val_counts.empty else "N/A"
        top_freq = int(val_counts.iloc[0]) if not val_counts.empty else 0

        profile[col] = {
            "cardinality": int(series.nunique()),
            "top_value": str(top_val),
            "top_frequency": top_freq,
            "top_percentage": float((top_freq / len(series)) * 100.0) if len(series) > 0 else 0.0,
            "missing_count": int(df[col].isnull().sum()),
        }
    return profile


def run_data_profiling(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs end-to-end data audit on the DataFrame.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())

    # Missing values
    missing_counts = df.isnull().sum()
    missing_summary = {
        col: {"missing": int(cnt), "percentage": float((cnt / total_rows) * 100.0)}
        for col, cnt in missing_counts.items()
        if cnt > 0
    }

    # Column type segregation
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number, "datetime64"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    num_profile = compute_numerical_profile(df, num_cols)
    cat_profile = compute_categorical_profile(df, cat_cols)

    # Correlations with target Profit if present
    target_correlations = {}
    if "Profit" in df.columns:
        profit_series = df["Profit"]
        for col in num_cols:
            if col != "Profit":
                clean_pair = df[[col, "Profit"]].dropna()
                pearson = float(clean_pair[col].corr(clean_pair["Profit"], method="pearson"))
                spearman = float(clean_pair[col].corr(clean_pair["Profit"], method="spearman"))
                target_correlations[col] = {
                    "pearson": round(pearson, 4),
                    "spearman": round(spearman, 4),
                }

    # Business data integrity checks
    integrity = {
        "negative_sales_count": int((df["Sales"] < 0).sum()) if "Sales" in df.columns else 0,
        "zero_sales_count": int((df["Sales"] == 0).sum()) if "Sales" in df.columns else 0,
        "negative_quantity_count": int((df["Quantity"] <= 0).sum()) if "Quantity" in df.columns else 0,
        "discount_out_of_bounds": int(((df["Discount"] < 0) | (df["Discount"] > 1.0)).sum()) if "Discount" in df.columns else 0,
        "loss_orders_count": int((df["Profit"] < 0).sum()) if "Profit" in df.columns else 0,
        "loss_orders_percentage": float(((df["Profit"] < 0).mean()) * 100.0) if "Profit" in df.columns else 0.0,
        "profitable_orders_count": int((df["Profit"] > 0).sum()) if "Profit" in df.columns else 0,
        "break_even_orders_count": int((df["Profit"] == 0).sum()) if "Profit" in df.columns else 0,
    }

    return {
        "summary": {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "duplicate_rows": duplicate_rows,
            "numeric_columns_count": len(num_cols),
            "categorical_columns_count": len(cat_cols),
            "date_columns_count": len(date_cols),
        },
        "missing_summary": missing_summary,
        "numerical_profile": num_profile,
        "categorical_profile": cat_profile,
        "target_correlations": target_correlations,
        "integrity_checks": integrity,
    }


def generate_profiling_visualizations(df: pd.DataFrame, figures_dir: Path) -> List[Path]:
    """
    Creates informative visual plots for distribution and relationship analysis.
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []

    # 1. Target Profit Distribution (Histogram + Boxplot)
    if "Profit" in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle("Order-Level Profit Distribution Analysis", fontsize=14, fontweight="bold")

        # Trim extreme visualization limits for readable histogram while preserving true data
        p_min, p_max = np.percentile(df["Profit"], 1), np.percentile(df["Profit"], 99)
        trimmed = df["Profit"][(df["Profit"] >= p_min) & (df["Profit"] <= p_max)]

        axes[0].hist(trimmed, bins=50, color="#2563eb", edgecolor="black", alpha=0.7)
        axes[0].axvline(0, color="red", linestyle="--", linewidth=1.5, label="Break-Even ($0)")
        axes[0].axvline(df["Profit"].mean(), color="green", linestyle="-", linewidth=1.5, label=f"Mean: ${df['Profit'].mean():.2f}")
        axes[0].axvline(df["Profit"].median(), color="orange", linestyle="-", linewidth=1.5, label=f"Median: ${df['Profit'].median():.2f}")
        axes[0].set_title("Profit Histogram (1st-99th Percentile)")
        axes[0].set_xlabel("Profit ($)")
        axes[0].set_ylabel("Order Frequency")
        axes[0].legend(loc="upper right")
        axes[0].grid(True, linestyle=":", alpha=0.6)

        axes[1].boxplot(df["Profit"], orientation="horizontal", patch_artist=True,
                        boxprops=dict(facecolor="#93c5fd", color="#1e40af"),
                        medianprops=dict(color="#b91c1c", linewidth=2))
        axes[1].set_title("Full Profit Range Boxplot (Outliers Visible)")
        axes[1].set_xlabel("Profit ($)")
        axes[1].grid(True, linestyle=":", alpha=0.6)

        plt.tight_layout()
        profit_dist_path = figures_dir / "profit_distribution.png"
        fig.savefig(profit_dist_path, dpi=200)
        plt.close(fig)
        generated_files.append(profit_dist_path)

    # 2. Discount vs Profit Boxplot
    if "Discount" in df.columns and "Profit" in df.columns:
        fig, ax = plt.subplots(figsize=(10, 5))
        # Group discounts into bins
        discount_bins = pd.cut(df["Discount"], bins=[-0.01, 0.0, 0.2, 0.4, 0.7, 1.0],
                               labels=["0% (None)", "1-20% (Low)", "21-40% (Medium)", "41-70% (High)", ">70% (Steep)"])
        df_temp = df.copy()
        df_temp["Discount Bracket"] = discount_bins

        bracket_groups = [group["Profit"].values for _, group in df_temp.groupby("Discount Bracket", observed=False)]
        ax.boxplot(bracket_groups, tick_labels=["0% (None)", "1-20% (Low)", "21-40% (Medium)", "41-70% (High)", ">70% (Steep)"],
                   showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor="#cbd5e1", color="#334155"),
                   medianprops=dict(color="#dc2626", linewidth=2))
        ax.axhline(0, color="red", linestyle="--", linewidth=1.2, label="Break-Even ($0)")
        ax.set_title("Profit by Discount Tier (Interquartile Ranges, Outliers Hidden for Readability)", fontweight="bold")
        ax.set_xlabel("Discount Tier")
        ax.set_ylabel("Profit ($)")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.6)

        plt.tight_layout()
        discount_profit_path = figures_dir / "discount_vs_profit.png"
        fig.savefig(discount_profit_path, dpi=200)
        plt.close(fig)
        generated_files.append(discount_profit_path)

    # 3. Correlation Heatmap
    num_cols = [c for c in ["Sales", "Quantity", "Discount", "Profit", "Shipping Days", "Order Year"] if c in df.columns]
    if len(num_cols) >= 3:
        corr_matrix = df[num_cols].corr(method="pearson").round(2)
        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.matshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
        fig.colorbar(cax)

        ax.set_xticks(range(len(num_cols)))
        ax.set_yticks(range(len(num_cols)))
        ax.set_xticklabels(num_cols, rotation=45, ha="left")
        ax.set_yticklabels(num_cols)

        # Annotate values
        for i in range(len(num_cols)):
            for j in range(len(num_cols)):
                val = corr_matrix.iloc[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color="white" if abs(val) > 0.4 else "black", fontweight="bold")

        ax.set_title("Pearson Correlation Heatmap (Key Numeric Attributes)", pad=30, fontweight="bold")
        plt.tight_layout()
        corr_path = figures_dir / "correlation_matrix.png"
        fig.savefig(corr_path, dpi=200)
        plt.close(fig)
        generated_files.append(corr_path)

    # 4. Sales vs Profit Scatter by Discount
    if "Sales" in df.columns and "Profit" in df.columns and "Discount" in df.columns:
        fig, ax = plt.subplots(figsize=(9, 5))
        scatter = ax.scatter(df["Sales"], df["Profit"], c=df["Discount"], cmap="viridis", alpha=0.6, edgecolors="none")
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label("Discount Rate (0.0 to 1.0)")
        ax.axhline(0, color="red", linestyle="--", alpha=0.8, label="Break-Even ($0)")
        ax.set_title("Order Sales vs Profit (Colored by Discount Rate)", fontweight="bold")
        ax.set_xlabel("Sales ($)")
        ax.set_ylabel("Profit ($)")
        ax.set_xlim(left=0, right=min(10000, df["Sales"].quantile(0.999)))
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.5)

        plt.tight_layout()
        scatter_path = figures_dir / "sales_profit_scatter.png"
        fig.savefig(scatter_path, dpi=200)
        plt.close(fig)
        generated_files.append(scatter_path)

    return generated_files


def generate_markdown_report(profile: Dict[str, Any], figures: List[Path], output_path: Path):
    """
    Renders an exhaustive, rigorous Markdown Data Quality & Profiling Report.
    """
    summary = profile["summary"]
    integrity = profile["integrity_checks"]
    num_profile = profile["numerical_profile"]
    cat_profile = profile["categorical_profile"]
    corrs = profile["target_correlations"]

    md = []
    md.append("# Data Quality, Preprocessing & Exploratory Profiling Report\n")
    md.append("## 1. Executive Summary & Dataset Dimensions\n")
    md.append(f"- **Total Records (Rows)**: {summary['total_rows']:,}")
    md.append(f"- **Total Attributes (Columns)**: {summary['total_columns']}")
    md.append(f"- **Duplicate Rows**: {summary['duplicate_rows']}")
    md.append(f"- **Numerical Attributes**: {summary['numeric_columns_count']}")
    md.append(f"- **Categorical Attributes**: {summary['categorical_columns_count']}")
    md.append(f"- **Datetime Attributes**: {summary['date_columns_count']}\n")

    md.append("## 2. Data Integrity & Domain Business Rule Audits\n")
    md.append("| Integrity Check | Observed Value | Expected Domain Rule | Status |")
    md.append("| :--- | :---: | :---: | :---: |")
    md.append(f"| Negative Sales | {integrity['negative_sales_count']} | 0 (Sales >= 0) | {'PASS' if integrity['negative_sales_count'] == 0 else 'FAIL'} |")
    md.append(f"| Invalid Quantities (<=0) | {integrity['negative_quantity_count']} | 0 (Quantity >= 1) | {'PASS' if integrity['negative_quantity_count'] == 0 else 'FAIL'} |")
    md.append(f"| Discount Out of [0, 1] Range | {integrity['discount_out_of_bounds']} | 0 (0 <= Discount <= 1.0) | {'PASS' if integrity['discount_out_of_bounds'] == 0 else 'FAIL'} |")
    md.append(f"| Loss-Making Orders (Profit < 0) | {integrity['loss_orders_count']} ({integrity['loss_orders_percentage']:.2f}%) | Business reality (heavy discounting) | EXPECTED |")
    md.append(f"| Profitable Orders (Profit > 0) | {integrity['profitable_orders_count']} | Normal retail operations | EXPECTED |")
    md.append(f"| Break-Even Orders (Profit = 0) | {integrity['break_even_orders_count']} | Zero profit margin | EXPECTED |\n")

    md.append("> **Important Preprocessing Decision Note on Loss-Making Orders:**")
    md.append("> Negative profit values represent genuine retail losses primarily induced by aggressive regional discounting.")
    md.append("> **They are NOT data corruption or entry errors and MUST NOT be dropped or imputed.**")
    md.append("> Deleting negative profit transactions would induce survival bias and invalidate predictive modeling.\n")

    md.append("## 3. Missing Value & Nullness Analysis\n")
    if not profile["missing_summary"]:
        md.append("No missing or null values were identified across the cleaned analytical dataset.\n")
    else:
        md.append("| Column | Missing Count | Missing Percentage |")
        md.append("| :--- | :---: | :---: |")
        for col, data in profile["missing_summary"].items():
            md.append(f"| {col} | {data['missing']} | {data['percentage']:.2f}% |")
        md.append("\n")

    md.append("## 4. Numerical Distributions, Skewness & Outlier Analysis\n")
    md.append("| Feature | Mean | Median (Q50) | Std Dev | Min | Max | Skewness | Kurtosis | Outliers (IQR) | Outlier % |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for col, stat in num_profile.items():
        md.append(
            f"| **{col}** | {stat['mean']:.2f} | {stat['median']:.2f} | {stat['std']:.2f} | "
            f"{stat['min']:.2f} | {stat['max']:.2f} | {stat['skewness']:.2f} | {stat['kurtosis']:.2f} | "
            f"{stat['outlier_count']} | {stat['outlier_percentage']:.2f}% |"
        )
    md.append("\n")

    md.append("### Distribution Findings & Outlier Treatment Rationale\n")
    md.append("- **Profit Target Distribution**: Highly leptokurtic and skewed (positive and negative extremes). Minimum is -$6,599.98 and maximum is $8,399.98. Tree-based regressors with Huber or absolute error loss are robust to these heavy tails without arbitrary record truncation.")
    md.append("- **Sales Outliers**: Large commercial orders (e.g. Cisco telepresence systems, Canon copiers) generate high revenue outliers. These represent authentic transactions in the B2B customer segment.\n")

    md.append("## 5. Feature Relationships & Target Correlations (Profit)\n")
    md.append("| Numerical Feature | Pearson Correlation (Linear) | Spearman Correlation (Monotonic Rank) | Business Interpretation |")
    md.append("| :--- | :---: | :---: | :--- |")
    for col, c in corrs.items():
        interp = ""
        if col == "Sales":
            interp = "Moderate positive association; higher sales often yield higher gross profit, modulated by margin."
        elif col == "Discount":
            interp = "Negative correlation; higher discount rates directly erode margin and trigger steep order losses."
        elif col == "Quantity":
            interp = "Weak correlation; volume alone does not guarantee profit without considering unit margin and discount."
        elif col == "Shipping Days":
            interp = "Negligible linear relationship with profit margin."
        else:
            interp = "Auxiliary calendar / engineered metric."
        md.append(f"| {col} | {c['pearson']:+.4f} | {c['spearman']:+.4f} | {interp} |")
    md.append("\n")

    md.append("## 6. Categorical Cardinality & Feature Structure\n")
    md.append("| Categorical Feature | Cardinality (Unique) | Top Category | Top Frequency | Top % | Preprocessing Strategy |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    for col, c in cat_profile.items():
        strategy = ""
        if c["cardinality"] <= 10:
            strategy = "One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`)"
        elif c["cardinality"] <= 50:
            strategy = "One-Hot Encoding or Frequency/Target Encoding"
        elif "ID" in col or "Name" in col:
            strategy = "Exclude from ML features to prevent high-cardinality memorization & leakage"
        else:
            strategy = "Standard categorical encoding"
        md.append(f"| {col} | {c['cardinality']} | {c['top_value']} | {c['top_frequency']} | {c['top_percentage']:.1f}% | {strategy} |")
    md.append("\n")

    md.append("## 7. Data Leakage & Feature Selection Directives\n")
    md.append("For predictive modeling (Target: `Profit`), the following features are strictly categorized:\n")
    md.append("1. **Target Feature**: `Profit` (Excluded from training inputs).")
    md.append("2. **Target Leakage Features (Must be Excluded)**:")
    md.append("   - `Profit Margin` (`Profit / Sales` mathematically leaks the target directly).")
    md.append("   - `Profit Bucket` (Derived directly from profit thresholds).")
    md.append("3. **Post-Fulfillment Features (Excluded for At-Order Inference)**:")
    md.append("   - `Ship Date`, `Shipping Days` (Only finalized when package leaves warehouse).")
    md.append("4. **High-Cardinality Identifiers (Excluded to Prevent Memorization)**:")
    md.append("   - `Row ID`, `Order ID`, `Customer ID`, `Customer Name`, `Product ID`, `Product Name`.")
    md.append("5. **Legitimate Order-Time Predictors (Permitted Inputs)**:")
    md.append("   - `Sales`, `Quantity`, `Discount`, `Category`, `Sub-Category`, `Segment`, `Region`, `Ship Mode`, `Order Month`, `Order Day`.\n")

    md.append("## 8. Visual Evidence Artifacts\n")
    for fig in figures:
        md.append(f"- `reports/figures/{fig.name}`")
    md.append("\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    parser = argparse.ArgumentParser(description="Data Quality & Statistical Profiling")
    parser.add_argument("--input", default="data/cleaned/orders_clean.csv", help="Path to cleaned dataset")
    parser.add_argument("--output", default="reports/data_quality_report.md", help="Output path for report")
    parser.add_argument("--figures", default="reports/figures", help="Output directory for figures")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    figures_dir = Path(args.figures)

    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found at {input_path}")

    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")

    print("Executing statistical profiling...")
    profile = run_data_profiling(df)

    print("Generating profiling visualizations...")
    figures = generate_profiling_visualizations(df, figures_dir)
    print(f"Generated {len(figures)} figures in {figures_dir}.")

    print(f"Saving Markdown report to {output_path}...")
    generate_markdown_report(profile, figures, output_path)

    # Also save raw profile json for test verifications
    json_path = output_path.parent / "data_quality_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    print(f"Data quality metrics JSON saved to {json_path}.")
    print("Data Quality & Profiling completed successfully.")


if __name__ == "__main__":
    main()
