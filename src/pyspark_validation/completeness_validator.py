import logging
from typing import Any, Dict, List, Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType


logger = logging.getLogger(__name__)


def validate_completeness(
    df: DataFrame,
    dataset_name: str,
    required_columns: Optional[List[str]] = None,
    max_missing_percentage: float = 0.0,
    missing_placeholders: Optional[List[str]] = None,
    sample_size: int = 5,
) -> Dict[str, Any]:
    """
    Validate completeness of a PySpark DataFrame.

    Completeness answers:
        Are the required values present in the dataset?

    This validator detects:

    1. Actual Spark null values
       - null

    2. Empty strings
       - ""

    3. Whitespace-only strings
       - "   "

    4. Configured missing-value placeholders
       - "NaN"
       - "NULL"
       - "null"
       - "N/A"
       - "None"

    5. Required columns missing from the dataset

    6. Required columns containing missing values

    7. Columns exceeding the configured missing-value percentage threshold

    The DataFrame is not cleaned or modified. The validator only produces
    evidence about completeness issues.

    Args:
        df:
            PySpark DataFrame to validate.

        dataset_name:
            Human-readable dataset name.

        required_columns:
            Columns that must exist and must satisfy the completeness threshold.

        max_missing_percentage:
            Maximum allowed percentage of missing values per column.

        missing_placeholders:
            String values that should be interpreted as missing.

        sample_size:
            Maximum number of failed records to collect per affected column.

    Returns:
        Dictionary containing completeness results and PASS/FAIL status.
    """
    logger.info(
        "Running PySpark completeness validation for: %s",
        dataset_name,
    )

    required_columns = required_columns or []

    missing_placeholders = missing_placeholders or [
        "NaN",
        "nan",
        "NULL",
        "null",
        "N/A",
        "n/a",
        "None",
        "none",
    ]

    row_count = df.count()

    string_columns = {
        field.name
        for field in df.schema.fields
        if isinstance(field.dataType, StringType)
    }

    missing_conditions: Dict[str, Any] = {}
    aggregation_expressions = []

    for column_name in df.columns:
        column = F.col(column_name)

        if column_name in string_columns:
            trimmed_column = F.trim(column)

            missing_condition = (
                column.isNull()
                | (trimmed_column == "")
                | trimmed_column.isin(missing_placeholders)
            )
        else:
            missing_condition = column.isNull()

        missing_conditions[column_name] = missing_condition

        aggregation_expressions.append(
            F.sum(
                F.when(missing_condition, 1).otherwise(0)
            ).alias(column_name)
        )

    missing_counts_row = df.agg(*aggregation_expressions).first()

    missing_counts = (
        missing_counts_row.asDict()
        if missing_counts_row is not None
        else {}
    )

    issue_details_by_column: Dict[str, Any] = {}

    for column_name in df.columns:
        missing_count = int(missing_counts.get(column_name, 0) or 0)

        missing_percentage = (
            round((missing_count / row_count) * 100, 2)
            if row_count > 0
            else 0.0
        )

        if missing_count > 0:
            sample_rows = [
                row.asDict(recursive=True)
                for row in (
                    df.filter(missing_conditions[column_name])
                    .limit(sample_size)
                    .collect()
                )
            ]

            issue_details_by_column[column_name] = {
                "missing_count": missing_count,
                "missing_percentage": missing_percentage,
                "sample_rows": sample_rows,
            }

    missing_required_columns = [
        column_name
        for column_name in required_columns
        if column_name not in df.columns
    ]

    required_column_issues: Dict[str, Any] = {}

    for column_name in required_columns:
        if column_name not in df.columns:
            required_column_issues[column_name] = {
                "issue": "required_column_missing_from_dataset"
            }
            continue

        details = issue_details_by_column.get(
            column_name,
            {
                "missing_count": 0,
                "missing_percentage": 0.0,
                "sample_rows": [],
            },
        )

        if details["missing_percentage"] > max_missing_percentage:
            required_column_issues[column_name] = {
                **details,
                "issue": "missing_percentage_exceeds_threshold",
            }

    columns_exceeding_threshold = {
        column_name: details
        for column_name, details in issue_details_by_column.items()
        if details["missing_percentage"] > max_missing_percentage
    }

    status = (
        "PASS"
        if not missing_required_columns
        and not required_column_issues
        else "FAIL"
    )

    logger.info(
        (
            "PySpark completeness validation completed | "
            "dataset=%s | status=%s | affected_columns=%s"
        ),
        dataset_name,
        status,
        len(issue_details_by_column),
    )

    return {
        "check_name": "pyspark_completeness_validation",
        "dataset_name": dataset_name,
        "status": status,
        "row_count": row_count,
        "required_columns": required_columns,
        "max_missing_percentage": max_missing_percentage,
        "missing_placeholders": missing_placeholders,
        "columns_with_completeness_issues": list(
            issue_details_by_column.keys()
        ),
        "issue_details_by_column": issue_details_by_column,
        "missing_required_columns": missing_required_columns,
        "required_column_issues": required_column_issues,
        "columns_exceeding_threshold": columns_exceeding_threshold,
    }