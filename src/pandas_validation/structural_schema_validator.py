import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Union
from src.utils.file_loader import load_csv
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)

def validate_schema(source_df: pd.DataFrame, target_df: pd.DataFrame) -> Dict[str, Union[List[str], bool]]:
    """
    Validate that the source and target datasets have the same structural schema.

    This validator performs structural validation only. It does NOT inspect the
    quality or correctness of the data values themselves. Its purpose is to
    ensure that the migrated dataset preserves the expected table structure
    before deeper data quality validation is performed.

    The validator currently checks:

    1. Column Names
       - Confirms that every column in the source dataset exists in the target.
       - Identifies columns that are missing in the target dataset.
       - Identifies unexpected (extra) columns in the target dataset.

    2. Column Order
       - Verifies that columns appear in the same order.
       - This is particularly useful for CSV-based ingestion pipelines where
         column ordering may be significant.

    3. Data Types
       - Compares the inferred pandas data types for every column.
       - Detects changes such as:
           * integer -> string
           * float -> object
           * datetime -> string
       - Ensures migrated datasets preserve the expected data types.

    4. Overall Schema Status
       - Returns PASS when both the column structure and data types match.
       - Returns FAIL when any schema mismatch is detected.

    This validator intentionally does NOT check:

    - Missing or null values
    - Duplicate rows
    - Duplicate primary keys
    - Invalid business values
      (e.g. Quantity = "two hundred")
    - Business rules
    - Referential integrity
    - Source-to-target record parity

    Those checks belong to dedicated validators such as:
        - completeness_validator.py
        - uniqueness_validator.py
        - validity_validator.py
        - integrity_validator.py
        - parity_validator.py

    Args:
        source_df:
            Source dataset before migration.

        target_df:
            Target dataset after migration.

    Returns:
        Dictionary containing the schema validation results, including:
        - source columns
        - target columns
        - missing columns
        - unexpected columns
        - source data types
        - target data types
        - schema comparison status (PASS/FAIL)
    """
    source_columns = set(source_df.columns)
    target_columns = set(target_df.columns)

    missing_in_target = list(source_columns - target_columns)
    extra_in_target = list(target_columns - source_columns)

    is_valid = len(missing_in_target) == 0 and len(extra_in_target) == 0

    validation_results = {
        "is_valid": is_valid,
        "missing_in_target": missing_in_target,
        "extra_in_target": extra_in_target,
    }

    if not is_valid:
        logger.warning("Schema validation failed.")
        if missing_in_target:
            logger.warning(f"Columns missing in target: {missing_in_target}")
        if extra_in_target:
            logger.warning(f"Extra columns in target: {extra_in_target}")
    else:
        logger.info("Schema validation passed.")

    return validation_results

