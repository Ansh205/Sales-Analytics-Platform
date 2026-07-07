"""
load_data.py

Loads the Global Superstore dataset from Excel
and returns individual DataFrames.

Author: Ansh Bansal
Project: Sales Analytics Platform
"""

from pathlib import Path
import pandas as pd


class DataLoader:
    """
    Loads all sheets from the Global Superstore dataset.
    """

    def __init__(self, file_path):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"\nDataset not found:\n{self.file_path}"
            )

    def get_sheet_names(self):
        """
        Return all sheet names.
        """
        excel = pd.ExcelFile(self.file_path)

        return excel.sheet_names

    def load_orders(self):

        return pd.read_excel(
            self.file_path,
            sheet_name="Orders"
        )

    def load_returns(self):

        return pd.read_excel(
            self.file_path,
            sheet_name="Returns"
        )

    def load_people(self):

        return pd.read_excel(
            self.file_path,
            sheet_name="People"
        )

    def load_all(self):

        orders = self.load_orders()
        returns = self.load_returns()
        people = self.load_people()

        return orders, returns, people