import logging
from typing import Dict, List, Union, Any, Optional
import pandas as pd
from utils.file_loader import load_csv
from utils.logger import setup_logger   

logger = logging.getLogger(__name__)


def validate_completeness(df: pd.DataFrame,dataset_name: str, required_columns: Optional[List[str]] = None,max_missing_percentage: float = 0.0,) -> Dict[str, Any]:
    """ Validate dataset completeness.

    This validator checks:
    - Null / NaN values
    - Empty strings: ""
    - Whitespace-only strings: "   "
    - Missing required columns
    - Missing values in required columns
    - Columns exceeding the allowed missing percentage threshold

    It does not clean or modify the dataset. It only reports issues."""
    
    required_columns = required_columns or []

    logger.info("Running completeness validation for dataset: %s", dataset_name)

    issue_details: Dict[str, Any] = {}
    required_column_issues: Dict[str, Any] = {}

    for column in df.columns:
        series = df[column]

        null_mask = series.isna()

        if series.dtype == "object":
            empty_mask = series.eq("")
            whitespace_mask = series.astype(str).str.fullmatch(r"\s+").fillna(False)
        else:
            empty_mask = pd.Series(False, index=df.index)
            whitespace_mask = pd.Series(False, index=df.index)

        combined_missing_mask = null_mask | empty_mask | whitespace_mask

        null_count = int(null_mask.sum())
        empty_count = int(empty_mask.sum())
        whitespace_count = int(whitespace_mask.sum())
        total_missing_count = int(combined_missing_mask.sum())
        missing_percentage = round((total_missing_count / len(df)) * 100, 2)

        if total_missing_count > 0:
            issue_details[column] = {
                "null_nan_count": null_count,
                "empty_string_count": empty_count,
                "whitespace_only_count": whitespace_count,
                "total_missing_count": total_missing_count,
                "missing_percentage": missing_percentage,
                "sample_missing_rows": df[combined_missing_mask]
                .head(5)
                .to_dict(orient="records"),
            }

    for column in required_columns:
        if column not in df.columns:
            required_column_issues[column] = {
                "issue": "required_column_missing_from_dataset"
            }
        elif column in issue_details:
            required_column_issues[column] = issue_details[column]
        else:
            required_column_issues[column] = {
                "total_missing_count": 0,
                "missing_percentage": 0.0,
                "status": "PASS",
            }

    columns_exceeding_threshold = {
        column: details
        for column, details in issue_details.items()
        if details["missing_percentage"] > max_missing_percentage
    }

    status = (
        "PASS"
        if not columns_exceeding_threshold
        and all(
            issue.get("total_missing_count", 0) == 0
            for issue in required_column_issues.values()
        )
        else "FAIL"
    )

    logger.info(
        "Completeness validation completed | dataset=%s | columns_with_issues=%s | status=%s",
        dataset_name,
        len(issue_details),
        status,
    )

    return {
        "check_name": "completeness_validation",
        "dataset_name": dataset_name,
        "status": status,
        "max_missing_percentage": max_missing_percentage,
        "columns_with_completeness_issues": list(issue_details.keys()),
        "issue_details_by_column": issue_details,
        "columns_exceeding_threshold": columns_exceeding_threshold,
        "required_column_issues": required_column_issues,
    }