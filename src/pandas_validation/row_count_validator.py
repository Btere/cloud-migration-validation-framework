import logging
from pathlib import Path
from typing import Dict, List, Union
import pandas as pd
from utils.file_loader import load_csv
from utils.logger import setup_logger

logger = logging.getLogger(__name__)

def validate_row_count_in_data(source_df: pd.DataFrame, target_df: pd.DataFrame) -> Dict[str, Union[int, bool]]:
    """
    Validate that the source and target datasets contain the same number of rows.

    This check is useful during migration validation because it provides a quick
    high-level indication of whether records may have been lost or added during
    transfer.

    Important:
        Matching row counts do NOT guarantee successful migration.
        A target dataset can have the same number of rows as the source while
        still containing missing records, duplicate records, or incorrect values.

    Args:
        source_df: Source dataset before migration.
        target_df: Target dataset after migration.

    Returns:
        Dictionary containing source row count, target row count, row count
        difference, and PASS/FAIL status.
    """
    source_count = len(source_df)
    target_count = len(target_df)
    difference = target_count - source_count

    status = "PASS" if source_count == target_count else "FAIL"

    logger.info(
        "Row count validation completed | source=%s | target=%s | difference=%s | status=%s",
        source_count,
        target_count,
        difference,
        status,
    )

    return {
        "check_name": "row_count_validation",
        "dataset_name": "source_vs_target",
    "source_count": source_count,
    "target_count": target_count,
    "difference": difference,
    "status": status,
    }