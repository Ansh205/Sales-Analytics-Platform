"""
data_validator.py

Validates datasets before exporting
and loading into SQL.
"""

import pandas as pd


class DataValidator:

    def __init__(self):
        pass

    def check_shape(self, df):

        print("=" * 50)
        print("DATASET SHAPE")
        print("=" * 50)

        print(df.shape)

    def check_missing_values(self, df):

        print("\nMissing Values")

        print("-" * 50)

        missing = df.isnull().sum()

        print(missing)

    def check_duplicates(self, df):

        print("\nDuplicate Rows")

        print("-" * 50)

        print(df.duplicated().sum())

    def check_data_types(self, df):

        print("\nData Types")

        print("-" * 50)

        print(df.dtypes)

    def sales_statistics(self, df):

        print("\nSales Statistics")

        print("-" * 50)

        print(df["Sales"].describe())

    def profit_statistics(self, df):

        print("\nProfit Statistics")

        print("-" * 50)

        print(df["Profit"].describe())

    def quantity_statistics(self, df):

        print("\nQuantity Statistics")

        print("-" * 50)

        print(df["Quantity"].describe())

    def discount_statistics(self, df):

        print("\nDiscount Statistics")

        print("-" * 50)

        print(df["Discount"].describe())

    def validate_orders(self, df):

        print("\n")

        print("=" * 60)
        print("VALIDATING ORDERS DATASET")
        print("=" * 60)

        self.check_shape(df)

        self.check_missing_values(df)

        self.check_duplicates(df)

        self.check_data_types(df)

        self.sales_statistics(df)

        self.profit_statistics(df)

        self.quantity_statistics(df)

        self.discount_statistics(df)

        print("\nValidation Completed")