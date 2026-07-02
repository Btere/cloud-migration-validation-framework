import logging
from typing import Any, Dict, Optional

import pandas as pd


logger = logging.getLogger(__name__)


def generate_data_profile(
    df: pd.DataFrame,
    dataset_name: str,
    primary_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a data profile for a pandas DataFrame.

    Args:
        df: Dataset as a pandas DataFrame.
        dataset_name: Human-readable dataset name.
        primary_key: Optional primary key column used to check key duplicates.

    Returns:
        Dictionary containing data profiling results.
    """
    logger.info("Generating data profile for dataset: %s", dataset_name)

    profile: Dict[str, Any] = {
        "dataset_name": dataset_name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 4),
        "missing_values": df.isna().sum().to_dict(),
        "missing_percentage": (df.isna().mean() * 100).round(2).to_dict(),
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_rows_preview": df[df.duplicated()].head(5).to_dict(orient="records"),
        "unique_values_per_column": df.nunique(dropna=True).to_dict(),
        "numeric_summary": df.describe(include="number").round(2).to_dict(),
        "categorical_summary": df.describe(include="object").to_dict(),
    }

    if primary_key and primary_key in df.columns:
        duplicate_keys = df[df.duplicated(subset=[primary_key], keep=False)]

        profile["primary_key"] = primary_key
        profile["duplicate_primary_key_count"] = int(
            df.duplicated(subset=[primary_key]).sum()
        )
        profile["duplicate_primary_key_preview"] = duplicate_keys.head(10).to_dict(
            orient="records"
        )

    elif primary_key:
        logger.warning(
            "Primary key '%s' not found in dataset '%s'",
            primary_key,
            dataset_name,
        )
        profile["primary_key"] = primary_key
        profile["primary_key_found"] = False

    logger.info(
        "Data profile completed | dataset=%s | rows=%s | columns=%s | duplicates=%s",
        dataset_name,
        profile["row_count"],
        profile["column_count"],
        profile["duplicate_row_count"],
    )

    return profile