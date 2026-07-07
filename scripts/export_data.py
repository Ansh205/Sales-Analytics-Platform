"""
export_data.py

Exports cleaned datasets.
"""

from pathlib import Path


class DataExporter:

    def __init__(self):

        self.output_folder = Path("../data/cleaned")

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def export_orders(self, df):

        output_file = self.output_folder / "orders_clean.csv"

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nOrders exported to\n{output_file}")

    def export_returns(self, df):

        output_file = self.output_folder / "returns_clean.csv"

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nReturns exported to\n{output_file}")

    def export_people(self, df):

        output_file = self.output_folder / "people_clean.csv"

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