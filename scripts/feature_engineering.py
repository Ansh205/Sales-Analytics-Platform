"""
feature_engineering.py

Creates new business features
for Power BI and SQL.
"""

import numpy as np
import pandas as pd


class FeatureEngineer:

    def __init__(self):
        pass

    # -------------------------
    # Date Features
    # -------------------------
    def create_date_features(self, df):

        df["Order Year"] = df["Order Date"].dt.year

        df["Order Month"] = df["Order Date"].dt.month_name()

        df["Order Quarter"] = df["Order Date"].dt.quarter

        df["Order Week"] = df["Order Date"].dt.isocalendar().week

        df["Order Day"] = df["Order Date"].dt.day_name()

        return df

    # -------------------------
    # Shipping Days
    # -------------------------
    def shipping_days(self, df):

        df["Shipping Days"] = (
            df["Ship Date"] -
            df["Order Date"]
        ).dt.days

        return df

    # -------------------------
    # Profit Margin
    # -------------------------
    def profit_margin(self, df):

        df["Profit Margin"] = np.where(
            df["Sales"] == 0,
            0,
            df["Profit"] / df["Sales"]
        )

        return df

    # -------------------------
    # Sales Bucket
    # -------------------------
    def sales_bucket(self, df):

        bins = [
            0,
            100,
            500,
            1000,
            df["Sales"].max()
        ]

        labels = [
            "Low",
            "Medium",
            "High",
            "Very High"
        ]

        df["Sales Bucket"] = pd.cut(
            df["Sales"],
            bins=bins,
            labels=labels,
            include_lowest=True
        )

        return df

    # -------------------------
    # Profit Bucket
    # -------------------------
    def profit_bucket(self, df):

        conditions = [

            df["Profit"] < 0,

            (df["Profit"] >= 0)
            &
            (df["Profit"] < 100),

            df["Profit"] >= 100

        ]

        choices = [

            "Loss",

            "Low Profit",

            "High Profit"

        ]

        df["Profit Bucket"] = np.select(
            conditions,
            choices,
            default="Unknown"
        )

        return df

    # -------------------------
    # Complete Feature Pipeline
    # -------------------------
    def create_features(self, df):

        print("\nCreating Features...\n")

        df = self.create_date_features(df)

        df = self.shipping_days(df)

        df = self.profit_margin(df)

        df = self.sales_bucket(df)

        df = self.profit_bucket(df)

        print("Feature Engineering Completed\n")

        return df
    
