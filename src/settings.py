"""
Global project configuration.

This module centralizes all project paths so that every module
(main.py, pyspark_main.py, validators, report generation, etc.)
imports paths from one location.

Benefits:
---------
- Avoids hard-coded absolute paths.
- Makes the project portable across different computers.
- Makes renaming folders much easier.
- Provides a single source of truth for project resources.
"""

from pathlib import Path

# =============================================================================
# PROJECT ROOT
# =============================================================================

# settings.py -> src -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =============================================================================
# PROJECT DIRECTORIES
# =============================================================================

CONFIG_DIR = PROJECT_ROOT / "configs"

DATASET_DIR = PROJECT_ROOT / "dataset"
SOURCE_DATASET_DIR = DATASET_DIR / "source"
TARGET_DATASET_DIR = DATASET_DIR / "target"

REPORT_DIR = PROJECT_ROOT / "reports"

SQL_DIR = PROJECT_ROOT / "sql"

NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

TEST_DIR = PROJECT_ROOT / "tests"


# =============================================================================
# CONFIGURATION FILES
# =============================================================================

VALIDATION_RULES_PATH = CONFIG_DIR / "validation_rules.yaml"

AWS_CONFIG_PATH = CONFIG_DIR / "aws_config.yaml"

GCP_CONFIG_PATH = CONFIG_DIR / "gcp_config.yaml"


# =============================================================================
# DATASETS
# =============================================================================

# Warehouse Inventory Dataset
SOURCE_WAREHOUSE_DATASET_PATH = (
    SOURCE_DATASET_DIR / "warehouse_messy.csv"
)

TARGET_WAREHOUSE_DATASET_PATH = (
    TARGET_DATASET_DIR / "warehouse_messy.csv"
)

# Review Dataset
SOURCE_REVIEW_DATASET_PATH = (
    SOURCE_DATASET_DIR / "source_reviews.csv"
)

TARGET_REVIEW_DATASET_PATH = (
    TARGET_DATASET_DIR / "source_reviews.csv"
)

# Images
SOURCE_IMAGE_DIR = SOURCE_DATASET_DIR / "images"

TARGET_IMAGE_DIR = TARGET_DATASET_DIR / "images"


# =============================================================================
# REPORTS
# =============================================================================

WAREHOUSE_REPORT_PATH = (
    REPORT_DIR / "warehouse_validation_report.json"
)

REVIEW_REPORT_PATH = (
    REPORT_DIR / "review_validation_report.json"
)

IMAGE_REPORT_PATH = (
    REPORT_DIR / "image_validation_report.json"
)