import logging
from typing import List, Dict, Any, Optional
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)

def generate_data_profile(df: DataFrame,dataset_name: str,primary_key: Optional[str] = None,sample_size: int = 5,) -> Dict[str, Any]:
    """ Generate a high-level profile of a PySpark DataFrame.mData profiling helps us understand the shape, structure, completeness,
    uniqueness, and basic content of a dataset before applying validation rules.

    The profiler currently collects:

    1. Dataset shape
       - Number of rows
       - Number of columns

    2. Dataset structure
       - Column names
       - Spark data types
       - Complete Spark schema

    3. Completeness indicators
       - Null counts per column
       - Empty-string counts per string column
       - Whitespace-only counts per string column
       - Combined missing-value counts and percentages

    4. Cardinality
       - Approximate distinct-value count per column

    5. Primary-key information
       - Whether the configured primary key exists
       - Null primary-key count
       - Duplicate primary-key count
       - Sample duplicate primary-key records

    6. Dataset sample
       - A small number of records for inspection

    This function does not clean or modify the DataFrame. It only calculates
    descriptive information that can guide later validation checks.

    Args:
        df:
            PySpark DataFrame to profile.

        dataset_name:
            Human-readable name for the dataset, such as
            "source_warehouse" or "target_warehouse".

        primary_key:
            Optional column expected to uniquely identify each record.

        sample_size:
            Maximum number of sample records to return.

    Returns:
        Dictionary containing the calculated data profile.
    """
    
    logger.info("Generating PySpark data profile for: %s", dataset_name)

    row_count = df.count()
    column_count = len(df.columns)

    schema = {
        field.name: {
            "data_type": field.dataType.simpleString(),
            "nullable": field.nullable,
        }
        for field in df.schema.fields
    }

    string_columns = [
        field.name
        for field in df.schema.fields
        if field.dataType.simpleString() == "string"
    ]

    missing_expressions = []

    for column_name in df.columns:
        column = F.col(column_name)

        if column_name in string_columns:
            missing_condition = (
                column.isNull()
                | (column == "")
                | (F.trim(column) == "")
            )
        else:
            missing_condition = column.isNull()

        missing_expressions.append(
            F.sum(
                F.when(missing_condition, 1).otherwise(0)
            ).alias(f"{column_name}__missing_count")
        )

    missing_row = df.agg(*missing_expressions).first()
    missing_results = missing_row.asDict() if missing_row else {}

    missing_count_per_column: Dict[str, int] = {}
    missing_percentage_per_column: Dict[str, float] = {}

    for column_name in df.columns:
        missing_count = int(
            missing_results.get(f"{column_name}__missing_count", 0)
        )

        missing_count_per_column[column_name] = missing_count

        missing_percentage_per_column[column_name] = (
            round((missing_count / row_count) * 100, 2)
            if row_count > 0
            else 0.0
        )

    distinct_expressions = [
        F.approx_count_distinct(F.col(column_name)).alias(
            f"{column_name}__distinct_count"
        )
        for column_name in df.columns
    ]

    distinct_row = df.agg(*distinct_expressions).first()
    distinct_results = distinct_row.asDict() if distinct_row else {}

    approximate_distinct_count_per_column = {
        column_name: int(
            distinct_results.get(
                f"{column_name}__distinct_count",
                0,
            )
        )
        for column_name in df.columns
    }

    profile: Dict[str, Any] = {
        "profile_name": "data_profile",
        "dataset_name": dataset_name,
        "row_count": row_count,
        "column_count": column_count,
        "columns": df.columns,
        "data_types": dict(df.dtypes),
        "schema": schema,
        "missing_count_per_column": missing_count_per_column,
        "missing_percentage_per_column": missing_percentage_per_column,
        "columns_with_missing_values": [
            column_name
            for column_name, count in missing_count_per_column.items()
            if count > 0
        ],
        "approximate_distinct_count_per_column": (
            approximate_distinct_count_per_column
        ),
        "sample_records": [
            row.asDict(recursive=True)
            for row in df.limit(sample_size).collect()
        ],
    }

    if primary_key is not None:
        profile["primary_key"] = primary_key

        if primary_key not in df.columns:
            profile["primary_key_found"] = False
            profile["primary_key_issue"] = (
                "Primary-key column is missing from the dataset."
            )

            logger.warning(
                "Primary key '%s' was not found in dataset '%s'",
                primary_key,
                dataset_name,
            )

        else:
            profile["primary_key_found"] = True

            null_primary_key_count = df.filter(
                F.col(primary_key).isNull()
            ).count()

            duplicate_primary_keys_df = (
                df.groupBy(primary_key)
                .count()
                .filter(F.col("count") > 1)
            )

            duplicate_primary_key_group_count = (
                duplicate_primary_keys_df.count()
            )

            duplicate_primary_key_record_count = (
                duplicate_primary_keys_df
                .select(
                    F.sum(F.col("count") - 1).alias(
                        "duplicate_record_count"
                    )
                )
                .first()
            )

            duplicate_record_count = (
                int(
                    duplicate_primary_key_record_count[
                        "duplicate_record_count"
                    ]
                )
                if duplicate_primary_key_record_count
                and duplicate_primary_key_record_count[
                    "duplicate_record_count"
                ]
                is not None
                else 0
            )

            profile.update(
                {
                    "null_primary_key_count": (
                        null_primary_key_count
                    ),
                    "duplicate_primary_key_group_count": (
                        duplicate_primary_key_group_count
                    ),
                    "duplicate_primary_key_record_count": (
                        duplicate_record_count
                    ),
                    "duplicate_primary_key_preview": [
                        row.asDict(recursive=True)
                        for row in duplicate_primary_keys_df
                        .limit(sample_size)
                        .collect()
                    ],
                }
            )

    logger.info(
        (
            "PySpark data profile completed | "
            "dataset=%s | rows=%s | columns=%s"
        ),
        dataset_name,
        row_count,
        column_count,
    )

    return profile
