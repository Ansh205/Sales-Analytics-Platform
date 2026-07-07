"""
report_generator.py

Automatically generates
Data Quality Report.
"""

from config import REPORT_FILE


class ReportGenerator:

    def __init__(self):

        REPORT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate(self, df):

        report = f"""
# Data Quality Report

## Dataset Summary

Rows : {len(df)}

Columns : {len(df.columns)}

---

## Missing Values

{df.isnull().sum().to_markdown()}

---

## Duplicate Rows

{df.duplicated().sum()}

---

## Data Types

{df.dtypes.to_markdown()}

---

## Sales Statistics

{df['Sales'].describe().to_markdown()}

---

## Profit Statistics

{df['Profit'].describe().to_markdown()}

---

## Quantity Statistics

{df['Quantity'].describe().to_markdown()}

---

## Discount Statistics

{df['Discount'].describe().to_markdown()}

"""

        with open(REPORT_FILE, "w", encoding="utf-8") as f:

            f.write(report)

        print("\nData Quality Report Generated")