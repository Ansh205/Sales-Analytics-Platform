"""
run_etl.py

Main ETL pipeline.

Phase 2
"""

from load_data import DataLoader


def main():

    print("=" * 60)
    print("Sales Analytics Platform")
    print("ETL Pipeline Started")
    print("=" * 60)

    dataset_path = "../data/raw/Global_Superstore.xls"

    loader = DataLoader(dataset_path)

    print("\nLoading Dataset...\n")

    orders, returns, people = loader.load_all()

    print("Dataset Loaded Successfully\n")

    print(f"Orders Shape  : {orders.shape}")
    print(f"Returns Shape : {returns.shape}")
    print(f"People Shape  : {people.shape}")

    print("\nColumns in Orders:\n")

    for column in orders.columns:
        print(column)

    print("\nETL Step 1 Completed")


if __name__ == "__main__":
    main()