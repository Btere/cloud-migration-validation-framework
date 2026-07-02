import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Union
from utils.file_loader import load_csv
from utils.logger import setup_logger

logger = logging.getLogger(__name__)

def validate_schema(source_df: pd.DataFrame, target_df: pd.DataFrame) -> Dict[str, Union[List[str], bool]]:
    """
    Validate the schema of the source and target DataFrames.

    Args:
        source_df (pd.DataFrame): The source DataFrame.
        target_df (pd.DataFrame): The target DataFrame.

    Returns:
        Dict[str, Union[List[str], bool]]: A dictionary containing the validation results.
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

