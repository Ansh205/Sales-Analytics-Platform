"""
clean_data.py

Contains all cleaning functions
for the Sales Analytics Platform.
"""

import pandas as pd


class DataCleaner:

    def __init__(self):
        pass

    # -----------------------------
    # Remove Duplicate Rows
    # -----------------------------
    def remove_duplicates(self, df):

        before = len(df)

        df = df.drop_duplicates()

        after = len(df)

        print(f"Duplicates Removed : {before-after}")

        return df

    # -----------------------------
    # Remove Extra Spaces
    # -----------------------------
    def strip_whitespace(self, df):

        object_columns = df.select_dtypes(include="object").columns

        for col in object_columns:
            df[col] = df[col].str.strip()

        return df

    # -----------------------------
    # Standardize Text
    # -----------------------------
    def standardize_text(self, df):

        object_columns = df.select_dtypes(include="object").columns

        for col in object_columns:
            df[col] = df[col].str.title()

        return df

    # -----------------------------
    # Convert Date Columns
    # -----------------------------
    def convert_dates(self, df):

        date_columns = [
            "Order Date",
            "Ship Date"
        ]

        for col in date_columns:

            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        return df

    # -----------------------------
    # Check Missing Values
    # -----------------------------
    def check_missing_values(self, df):

        print("\nMissing Values\n")

        print(df.isnull().sum())

    # -----------------------------
    # Remove Invalid Sales
    # -----------------------------
    def remove_invalid_sales(self, df):

        before = len(df)

        df = df[df["Sales"] >= 0]

        after = len(df)

        print(f"Invalid Sales Removed : {before-after}")

        return df

    # -----------------------------
    # Remove Invalid Quantity
    # -----------------------------
    def remove_invalid_quantity(self, df):

        before = len(df)

        df = df[df["Quantity"] > 0]

        after = len(df)

        print(f"Invalid Quantity Removed : {before-after}")

        return df

    # -----------------------------
    # Discount Validation
    # -----------------------------
    def validate_discount(self, df):

        before = len(df)

        df = df[
            (df["Discount"] >= 0)
            &
            (df["Discount"] <= 1)
        ]

        after = len(df)

        print(f"Invalid Discount Rows : {before-after}")

        return df

    # -----------------------------
    # Complete Cleaning Pipeline
    # -----------------------------
    def clean_orders(self, df):

        print("\nCleaning Orders Dataset...\n")

        df = self.remove_duplicates(df)

        df = self.strip_whitespace(df)

        df = self.standardize_text(df)

        df = self.convert_dates(df)

        self.check_missing_values(df)

        df = self.remove_invalid_sales(df)

        df = self.remove_invalid_quantity(df)

        df = self.validate_discount(df)

        print("\nCleaning Completed\n")

        return df