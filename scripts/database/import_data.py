"""
import_data.py

Imports cleaned CSV files into PostgreSQL.
"""

from pathlib import Path

import pandas as pd

from scripts.database.database import engine
from scripts.database.database_manager import DatabaseManager


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FOLDER = PROJECT_ROOT / "data" / "cleaned"


class DataImporter:

    def __init__(self):

        self.db = DatabaseManager()

        self.orders_file = DATA_FOLDER / "orders_clean.csv"

        self.returns_file = DATA_FOLDER / "returns_clean.csv"

        self.people_file = DATA_FOLDER / "people_clean.csv"

    # --------------------------------------------------

    def read_orders(self):

        print("Reading Orders...")

        return pd.read_csv(
            self.orders_file,
            parse_dates=["Order Date", "Ship Date"]
        )

    # --------------------------------------------------

    def read_returns(self):

        print("Reading Returns...")

        return pd.read_csv(self.returns_file)

    # --------------------------------------------------

    def read_people(self):

        print("Reading People...")

        return pd.read_csv(self.people_file)

    # --------------------------------------------------

    def truncate_tables(self):

        print("\nCleaning Database Tables...\n")

        self.db.truncate_table("orders")

        self.db.truncate_table("returns")

        self.db.truncate_table("people")

    # --------------------------------------------------

    def import_orders(self):

        df = self.read_orders()

        print("Importing Orders...")

        df.columns = [
            c.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            for c in df.columns
        ]

        df.to_sql(
            "orders",
            engine,
            if_exists="append",
            index=False
        )

        print(f"{len(df)} rows inserted.")

    # --------------------------------------------------

    def import_returns(self):

        df = self.read_returns()

        print("Importing Returns...")

        df.columns = [
            c.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            for c in df.columns
        ]

        df.to_sql(
            "returns",
            engine,
            if_exists="append",
            index=False
        )

        print(f"{len(df)} rows inserted.")

    # --------------------------------------------------

    def import_people(self):

        df = self.read_people()

        print("Importing People...")

        df.columns = [
            c.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            for c in df.columns
        ]

        df.to_sql(
            "people",
            engine,
            if_exists="append",
            index=False
        )

        print(f"{len(df)} rows inserted.")

    # --------------------------------------------------

    def import_all(self):

        self.truncate_tables()

        self.import_orders()

        self.import_returns()

        self.import_people()

        print("\nData Imported Successfully!")