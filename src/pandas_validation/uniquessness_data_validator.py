import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from src.utils.file_loader import load_csv
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)


def validate_unique_data_without_duplicates(df: pd.DataFrame,dataset_name: str,primary_key: Optional[str] = None,business_keys: Optional[List[str]] = None,) -> Dict[str, Any]:
    """ Validate uniqueness of records in a dataset.

    This validator checks:
    - Duplicate full rows
    - Duplicate primary key values
    - Duplicate business key combinations

    It does not remove duplicates. It only reports them."""
    
    business_keys = business_keys or []

    logger.info("Running uniqueness validation for dataset: %s", dataset_name)

    duplicate_rows = df[df.duplicated(keep=False)]

    result: Dict[str, Any] = {
        "check_name": "uniqueness_validation",
        "dataset_name": dataset_name,
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_rows_preview": duplicate_rows.head(10).to_dict(orient="records"),
        "primary_key": primary_key,
        "primary_key_duplicate_count": None,
        "primary_key_duplicate_preview": [],
        "business_keys": business_keys,
        "business_key_duplicate_count": None,
        "business_key_duplicate_preview": [],
    }

    if primary_key:
        if primary_key not in df.columns:
            result["primary_key_issue"] = "primary_key_column_missing"
        else:
            pk_duplicates = df[df.duplicated(subset=[primary_key], keep=False)]
            result["primary_key_duplicate_count"] = int(
                df.duplicated(subset=[primary_key]).sum()
            )
            result["primary_key_duplicate_preview"] = pk_duplicates.head(10).to_dict(
                orient="records"
            )

    if business_keys:
        missing_business_keys = [col for col in business_keys if col not in df.columns]

        if missing_business_keys:
            result["business_key_issue"] = {
                "missing_business_key_columns": missing_business_keys
            }
        else:
            business_duplicates = df[
                df.duplicated(subset=business_keys, keep=False)
            ]

            result["business_key_duplicate_count"] = int(
                df.duplicated(subset=business_keys).sum()
            )
            result["business_key_duplicate_preview"] = business_duplicates.head(10).to_dict(
                orient="records"
            )

    has_duplicate_rows = result["duplicate_row_count"] > 0
    has_duplicate_primary_keys = (
        result["primary_key_duplicate_count"] is not None
        and result["primary_key_duplicate_count"] > 0
    )
    has_duplicate_business_keys = (
        result["business_key_duplicate_count"] is not None
        and result["business_key_duplicate_count"] > 0
    )

    result["status"] = (
        "FAIL"
        if has_duplicate_rows
        or has_duplicate_primary_keys
        or has_duplicate_business_keys
        else "PASS"
    )

    logger.info(
        "Uniqueness validation completed | dataset=%s | status=%s",
        dataset_name,
        result["status"],
    )

    return result