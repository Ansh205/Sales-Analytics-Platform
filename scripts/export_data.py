"""
export_data.py

Exports cleaned datasets.
"""

from config import (
    CLEAN_DATA,
    ORDERS_OUTPUT,
    RETURNS_OUTPUT,
    PEOPLE_OUTPUT
)

class DataExporter:

    def __init__(self):

        self.output_folder = CLEAN_DATA

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def export_orders(self, df):

        output_file = ORDERS_OUTPUT

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nOrders exported to\n{output_file}")

    def export_returns(self, df):

        output_file = RETURNS_OUTPUT

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nReturns exported to\n{output_file}")

    def export_people(self, df):

        output_file = PEOPLE_OUTPUT

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nPeople exported to\n{output_file}")

    def export_all(
        self,
        orders,
        returns,
        people
    ):

        self.export_orders(orders)

        self.export_returns(returns)

        self.export_people(people)

        print("\nAll datasets exported successfully.")