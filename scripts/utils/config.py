from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Folders
DATA_FOLDER = PROJECT_ROOT / "data"

RAW_DATA = DATA_FOLDER / "raw"

CLEAN_DATA = DATA_FOLDER / "cleaned"

REPORTS = PROJECT_ROOT / "reports"

LOGS = PROJECT_ROOT / "logs"

# Dataset
DATASET_NAME = "Global_Superstore.xls"

DATASET_PATH = RAW_DATA / DATASET_NAME

# Export Files
ORDERS_OUTPUT = CLEAN_DATA / "orders_clean.csv"

RETURNS_OUTPUT = CLEAN_DATA / "returns_clean.csv"

PEOPLE_OUTPUT = CLEAN_DATA / "people_clean.csv"

REPORT_FILE = REPORTS / "data_quality_report.md"

LOG_FILE = LOGS / "etl.log"