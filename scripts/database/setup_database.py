"""
setup_database.py

Runs complete database setup.
"""

from pathlib import Path

from scripts.database.database_manager import DatabaseManager
from scripts.database.import_data import DataImporter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"


def main():

    print("=" * 60)

    print("Sales Analytics Platform")

    print("Database Setup")

    print("=" * 60)

    db = DatabaseManager()

    print("\nTesting Connection...\n")

    db.test_connection()

    print("\nChecking Tables...\n")

    if not db.table_exists("orders"):

        print("Tables not found.")

        print("Executing schema.sql...\n")

        db.execute_sql_file(SCHEMA_FILE)

    else:

        print("Tables already exist.\n")

    importer = DataImporter()

    importer.import_all()

    print("\nVerifying Row Counts\n")

    print("Orders :", db.row_count("orders"))

    print("Returns :", db.row_count("returns"))

    print("People :", db.row_count("people"))

    db.close()

    print("\nDatabase Ready!")

    print("=" * 60)


if __name__ == "__main__":

    main()