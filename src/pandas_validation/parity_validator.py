import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from src.utils.file_loader import load_csv
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)


import logging
from typing import Any, Dict, List

import pandas as pd


logger = logging.getLogger(__name__)


def validate_source_target_parity(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    primary_key: str,
    compare_columns: List[str],
) -> Dict[str, Any]:
    """
    Validate source-to-target record parity.

    Checks:
    - Records missing in target
    - Extra records in target
    - Value mismatches for selected columns

    Note:
        This validator expects the primary key to identify one record.
        If duplicate primary keys exist, they are reported separately and
        the first occurrence is used for value comparison.
    """
    logger.info("Running source-target parity validation")

    if primary_key not in source_df.columns:
        raise ValueError(f"Primary key missing from source: {primary_key}")

    if primary_key not in target_df.columns:
        raise ValueError(f"Primary key missing from target: {primary_key}")

    source_duplicate_keys = source_df[
        source_df.duplicated(subset=[primary_key], keep=False)
    ]

    target_duplicate_keys = target_df[
        target_df.duplicated(subset=[primary_key], keep=False)
    ]

    source_deduped = source_df.drop_duplicates(subset=[primary_key], keep="first")
    target_deduped = target_df.drop_duplicates(subset=[primary_key], keep="first")

    source_keys = set(source_deduped[primary_key])
    target_keys = set(target_deduped[primary_key])

    missing_keys_in_target = sorted(list(source_keys - target_keys))
    extra_keys_in_target = sorted(list(target_keys - source_keys))

    source_indexed = source_deduped.set_index(primary_key)
    target_indexed = target_deduped.set_index(primary_key)

    common_keys = source_keys.intersection(target_keys)

    mismatches = []

    for key in common_keys:
        for column in compare_columns:
            if column not in source_indexed.columns or column not in target_indexed.columns:
                continue

            source_value = source_indexed.at[key, column]
            target_value = target_indexed.at[key, column]

            if pd.isna(source_value) and pd.isna(target_value):
                continue

            if str(source_value) != str(target_value):
                mismatches.append(
                    {
                        primary_key: key,
                        "column": column,
                        "source_value": source_value,
                        "target_value": target_value,
                    }
                )

    status = (
        "PASS"
        if not missing_keys_in_target
        and not extra_keys_in_target
        and not mismatches
        and source_duplicate_keys.empty
        and target_duplicate_keys.empty
        else "FAIL"
    )

    return {
        "check_name": "source_target_parity_validation",
        "dataset_name": "source_vs_target",
        "status": status,
        "primary_key": primary_key,
        "source_duplicate_primary_key_count": int(source_duplicate_keys.shape[0]),
        "target_duplicate_primary_key_count": int(target_duplicate_keys.shape[0]),
        "source_duplicate_primary_key_preview": source_duplicate_keys.head(10).to_dict(
            orient="records"
        ),
        "target_duplicate_primary_key_preview": target_duplicate_keys.head(10).to_dict(
            orient="records"
        ),
        "missing_keys_in_target_count": len(missing_keys_in_target),
        "extra_keys_in_target_count": len(extra_keys_in_target),
        "value_mismatch_count": len(mismatches),
        "missing_keys_in_target": missing_keys_in_target[:20],
        "extra_keys_in_target": extra_keys_in_target[:20],
        "value_mismatches_preview": mismatches[:20],
    }