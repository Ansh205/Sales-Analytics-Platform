"""
database_manager.py

Handles all PostgreSQL operations.
"""

from pathlib import Path

from sqlalchemy import text

from scripts.database.database import (
    engine,
    SessionLocal
)


class DatabaseManager:

    def __init__(self):

        self.engine = engine

        self.session = SessionLocal()

    # ----------------------------------

    def execute_query(self, query):

        with self.engine.begin() as conn:

            result = conn.execute(text(query))

            return result

    # ----------------------------------

    def execute_sql_file(self, sql_file):

        sql_path = Path(sql_file)

        if not sql_path.exists():

            raise FileNotFoundError(
                f"{sql_file} not found."
            )

        with open(sql_path, "r", encoding="utf-8") as f:

            sql = f.read()

        with self.engine.begin() as conn:

            conn.execute(text(sql))

        print(f"Executed : {sql_file}")

    # ----------------------------------

    def truncate_table(self, table_name):

        query = (
            f"TRUNCATE TABLE {table_name} "
            f"RESTART IDENTITY CASCADE;"
        )

        self.execute_query(query)

        print(f"{table_name} truncated")

    # ----------------------------------

    def table_exists(self, table_name):

        query = f"""

        SELECT EXISTS (

            SELECT

            FROM information_schema.tables

            WHERE table_name='{table_name}'

        );

        """

        result = self.execute_query(query)

        return result.scalar()

    # ----------------------------------

    def row_count(self, table_name):

        query = f"""

        SELECT COUNT(*)

        FROM {table_name}

        """

        result = self.execute_query(query)

        return result.scalar()

    # ----------------------------------

    def test_connection(self):

        query = "SELECT version();"

        result = self.execute_query(query)

        print(result.fetchone()[0])

    # ----------------------------------

    def close(self):

        self.session.close()