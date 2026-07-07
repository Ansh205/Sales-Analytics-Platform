from load_data import DataLoader
from clean_data import DataCleaner
from feature_engineering import FeatureEngineer
from data_validator import DataValidator
from export_data import DataExporter
from logger import Logger
from report_generator import ReportGenerator
from config import DATASET_PATH

def main():

    print("=" * 60)
    print("Sales Analytics Platform ETL Pipeline")
    print("=" * 60)

    # -----------------------
    # Load Data
    # -----------------------

    loader = DataLoader(DATASET_PATH)
    Logger.info("Dataset Loaded Successfully")

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

    Logger.info("Feature Engineering Completed")

    # -----------------------
    # Validation
    # -----------------------

    validator = DataValidator()

    validator.validate_orders(orders)


    report = ReportGenerator()

    report.generate(orders)

    Logger.info("Data Quality Report Generated")

    # -----------------------
    # Export
    # -----------------------

    exporter = DataExporter()

    exporter.export_all(
        orders,
        returns,
        people
    )

    Logger.info("All datasets exported successfully.")

    print("\nETL Pipeline Completed Successfully")


if __name__ == "__main__":
    main()