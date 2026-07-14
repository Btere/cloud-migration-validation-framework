import logging
from typing import Any, Dict

from pyspark.sql import DataFrame


logger = logging.getLogger(__name__)


def validate_schema(
    source_df: DataFrame,
    target_df: DataFrame,
    check_column_order: bool = True,
    check_nullability: bool = False,
) -> Dict[str, Any]:
    """
    Validate structural schema parity between two PySpark DataFrames.

    This validator checks:

    1. Column presence
       - Columns missing from the target
       - Unexpected columns present in the target

    2. Column count
       - Whether source and target contain the same number of columns

    3. Column order
       - Whether columns appear in the same order
       - Optional because order may not matter for every pipeline

    4. Spark data types
       - Compares Spark-native data types such as:
         int, string, double, date, timestamp, boolean

    5. Nullability
       - Optionally compares whether each column is nullable
       - Disabled by default because some ingestion tools may infer
         nullability differently even when the data is otherwise compatible

    This validator does not inspect row values. It only validates the
    structure of the source and target DataFrames.

    Args:
        source_df:
            Source PySpark DataFrame before migration.

        target_df:
            Target PySpark DataFrame after migration.

        check_column_order:
            Whether source and target columns must appear in the same order.

        check_nullability:
            Whether source and target nullability settings must match.

    Returns:
        Dictionary containing schema validation results and PASS/FAIL status.
    """
    logger.info("Running PySpark schema validation")

    source_fields = {
        field.name: {
            "data_type": field.dataType.simpleString(),
            "nullable": field.nullable,
        }
        for field in source_df.schema.fields
    }

    target_fields = {
        field.name: {
            "data_type": field.dataType.simpleString(),
            "nullable": field.nullable,
        }
        for field in target_df.schema.fields
    }

    source_columns = source_df.columns
    target_columns = target_df.columns

    missing_columns_in_target = [
        column
        for column in source_columns
        if column not in target_columns
    ]

    extra_columns_in_target = [
        column
        for column in target_columns
        if column not in source_columns
    ]

    common_columns = [
        column
        for column in source_columns
        if column in target_columns
    ]

    data_type_mismatches = {}

    for column in common_columns:
        source_type = source_fields[column]["data_type"]
        target_type = target_fields[column]["data_type"]

        if source_type != target_type:
            data_type_mismatches[column] = {
                "source_type": source_type,
                "target_type": target_type,
            }

    nullability_mismatches = {}

    if check_nullability:
        for column in common_columns:
            source_nullable = source_fields[column]["nullable"]
            target_nullable = target_fields[column]["nullable"]

            if source_nullable != target_nullable:
                nullability_mismatches[column] = {
                    "source_nullable": source_nullable,
                    "target_nullable": target_nullable,
                }

    column_count_match = len(source_columns) == len(target_columns)

    column_order_match = source_columns == target_columns

    schema_passed = (
        not missing_columns_in_target
        and not extra_columns_in_target
        and not data_type_mismatches
        and column_count_match
        and (
            column_order_match
            if check_column_order
            else True
        )
        and (
            not nullability_mismatches
            if check_nullability
            else True
        )
    )

    status = "PASS" if schema_passed else "FAIL"

    logger.info(
        (
            "PySpark schema validation completed | "
            "status=%s | missing=%s | extra=%s | type_mismatches=%s"
        ),
        status,
        len(missing_columns_in_target),
        len(extra_columns_in_target),
        len(data_type_mismatches),
    )

    return {
        "check_name": "pyspark_schema_validation",
        "dataset_name": "source_vs_target",
        "status": status,
        "source_column_count": len(source_columns),
        "target_column_count": len(target_columns),
        "column_count_match": column_count_match,
        "source_columns": source_columns,
        "target_columns": target_columns,
        "missing_columns_in_target": missing_columns_in_target,
        "extra_columns_in_target": extra_columns_in_target,
        "column_order_checked": check_column_order,
        "column_order_match": column_order_match,
        "source_schema": source_fields,
        "target_schema": target_fields,
        "data_type_mismatches": data_type_mismatches,
        "nullability_checked": check_nullability,
        "nullability_mismatches": nullability_mismatches,
    }