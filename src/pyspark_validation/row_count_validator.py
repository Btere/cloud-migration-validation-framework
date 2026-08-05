import logging
from typing import Any, Dict
from pyspark.sql import DataFrame
from src.migration_automation_testing.pytest_concept. pytest_decorator import log_test

logger = logging.getLogger(__name__)

@log_test
def validate_row_count(source_df: DataFrame,target_df: DataFrame,) -> Dict[str, Any]:
    """Validate row-count parity between source and target PySpark DataFrames.

    This validator checks whether both datasets contain the same number of rows.

    It performs two Spark actions:
    - source_df.count()
    - target_df.count()

    Because count() scans the distributed datasets, this can be relatively
    expensive on very large tables. In production, the result may be reused,
    cached, or obtained from trusted pipeline telemetry where appropriate.

    Matching row counts do not prove that migration succeeded. Two datasets can
    have the same number of rows while still containing:
    - missing records,
    - duplicated records,
    - extra records,
    - value mismatches.

    Therefore, row-count validation should be combined with uniqueness and
    source-target parity checks.

    Args:
        source_df:
            Source PySpark DataFrame before migration.

        target_df:
            Target PySpark DataFrame after migration.

    Returns:
        Dictionary containing:
        - source row count,
        - target row count,
        - absolute and signed differences,
        - percentage difference,
        - PASS/FAIL status.
    """
    logger.info("Running PySpark row-count validation")

    source_count = source_df.count()
    target_count = target_df.count()

    signed_difference = target_count - source_count
    absolute_difference = abs(signed_difference)

    percentage_difference = (
        round((absolute_difference / source_count) * 100, 4)
        if source_count > 0
        else 0.0 if target_count == 0 else 100.0
    )

    status = "PASS" if source_count == target_count else "FAIL"

    logger.info(
        (
            "PySpark row-count validation completed | "
            "source=%s | target=%s | difference=%s | status=%s"
        ),
        source_count,
        target_count,
        signed_difference,
        status,
    )

    return {
        "check_name": "pyspark_row_count_validation",
        "dataset_name": "source_vs_target",
        "status": status,
        "source_row_count": source_count,
        "target_row_count": target_count,
        "signed_difference": signed_difference,
        "absolute_difference": absolute_difference,
        "percentage_difference": percentage_difference,
    }