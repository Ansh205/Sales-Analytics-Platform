"""
config.py

Central configuration file.
"""

from pathlib import Path

# ===============================
# Project Paths
# ===============================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA = PROJECT_ROOT / "data" / "raw"

CLEAN_DATA = PROJECT_ROOT / "data" / "cleaned"

REPORTS = PROJECT_ROOT / "reports"

LOGS = PROJECT_ROOT / "logs"

# ===============================
# Dataset
# ===============================

DATASET_NAME = "Global_Superstore.xls"

DATASET_PATH = RAW_DATA / DATASET_NAME

# ===============================
# Output Files
# ===============================

ORDERS_OUTPUT = CLEAN_DATA / "orders_clean.csv"

RETURNS_OUTPUT = CLEAN_DATA / "returns_clean.csv"

PEOPLE_OUTPUT = CLEAN_DATA / "people_clean.csv"

REPORT_FILE = REPORTS / "data_quality_report.md"

LOG_FILE = LOGS / "etl.log"