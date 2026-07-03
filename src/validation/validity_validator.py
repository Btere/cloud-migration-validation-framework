import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from utils.file_loader import load_csv
from utils.logger import setup_logger

logger = logging.getLogger(__name__)


def validate_validity(
    df: pd.DataFrame,
    dataset_name: str,
    rules: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate whether values follow expected formats and allowed data types.

    Checks:
    - Numeric columns contain numeric values
    - Date columns can be parsed as dates
    - Categorical columns contain allowed values
    """
    logger.info("Running validity validation for dataset: %s", dataset_name)

    issues = {}

    # Numeric checks
    numeric_columns = rules.get("numeric_columns", [])

    for column in numeric_columns:
        if column not in df.columns:
            issues[column] = {"issue": "column_missing"}
            continue

        converted = pd.to_numeric(df[column], errors="coerce")
        invalid_mask = converted.isna() & df[column].notna()

        if invalid_mask.any():
            issues[column] = {
                "issue": "invalid_numeric_values",
                "invalid_count": int(invalid_mask.sum()),
                "sample_rows": df[invalid_mask].head(5).to_dict(orient="records"),
            }

    # Date checks
    date_columns = rules.get("date_columns", [])

    for column in date_columns:
        if column not in df.columns:
            issues[column] = {"issue": "column_missing"}
            continue

        converted = pd.to_datetime(df[column], errors="coerce", dayfirst=True)
        invalid_mask = converted.isna() & df[column].notna()

        if invalid_mask.any():
            issues[column] = {
                "issue": "invalid_date_values",
                "invalid_count": int(invalid_mask.sum()),
                "sample_rows": df[invalid_mask].head(5).to_dict(orient="records"),
            }

    # Allowed value checks
    allowed_values = rules.get("allowed_values", {})

    for column, allowed in allowed_values.items():
        if column not in df.columns:
            issues[column] = {"issue": "column_missing"}
            continue

        invalid_mask = ~df[column].isin(allowed) & df[column].notna()

        if invalid_mask.any():
            issues[column] = {
                "issue": "invalid_categorical_values",
                "allowed_values": allowed,
                "invalid_count": int(invalid_mask.sum()),
                "sample_rows": df[invalid_mask].head(5).to_dict(orient="records"),
            }

    status = "PASS" if not issues else "FAIL"

    return {
        "check_name": "validity_validation",
        "dataset_name": dataset_name,
        "status": status,
        "issues": issues,
    }