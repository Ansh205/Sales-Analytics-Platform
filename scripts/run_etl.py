"""
run_etl.py

Main ETL pipeline.

Phase 2
"""

from load_data import DataLoader
from clean_data import DataCleaner
from feature_engineering import FeatureEngineer


def main():

    print("=" * 60)
    print("Sales Analytics Platform ETL")
    print("=" * 60)

    loader = DataLoader("../data/raw/Global_Superstore.xls")

    cleaner = DataCleaner()

    engineer = FeatureEngineer()

    orders, returns, people = loader.load_all()

    print("\nOriginal Shape")

    print(orders.shape)

    orders = cleaner.clean_orders(orders)

    orders = engineer.create_features(orders)

    print("\nFinal Shape")

    print(orders.shape)

    print("\nNew Columns Added")

    print(orders.columns.tolist()[-7:])

    print("\nPreview")

    print(orders.head())


if __name__ == "__main__":
    main()