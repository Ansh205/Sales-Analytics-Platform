from load_data import DataLoader
from clean_data import DataCleaner
from feature_engineering import FeatureEngineer
from data_validator import DataValidator
from export_data import DataExporter


def main():

    print("=" * 60)
    print("Sales Analytics Platform ETL Pipeline")
    print("=" * 60)

    # -----------------------
    # Load Data
    # -----------------------

    loader = DataLoader("../data/raw/Global_Superstore.xls")

    orders, returns, people = loader.load_all()

    # -----------------------
    # Cleaning
    # -----------------------

    cleaner = DataCleaner()

    orders = cleaner.clean_orders(orders)

    # -----------------------
    # Feature Engineering
    # -----------------------

    engineer = FeatureEngineer()

    orders = engineer.create_features(orders)

    # -----------------------
    # Validation
    # -----------------------

    validator = DataValidator()

    validator.validate_orders(orders)

    # -----------------------
    # Export
    # -----------------------

    exporter = DataExporter()

    exporter.export_all(
        orders,
        returns,
        people
    )

    print("\nETL Pipeline Completed Successfully")


if __name__ == "__main__":
    main()