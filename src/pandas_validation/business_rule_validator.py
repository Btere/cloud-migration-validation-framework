import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from utils.file_loader import load_csv
from utils.logger import setup_logger


logger = logging.getLogger(__name__)

def validate_business_rules(
    df: pd.DataFrame,
    dataset_name: str,
    rules: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate business-specific rules.

    Example warehouse rules:
    - Quantity must be >= 0
    - Price must be > 0
    - Last Restocked cannot be in the future
    """
    logger.info("Running business rule validation for dataset: %s", dataset_name)

    issues = {}

    quantity_column = rules.get("quantity_column")
    quantity_min = rules.get("quantity_min")

    if quantity_column and quantity_column in df.columns:
        quantity_numeric = pd.to_numeric(df[quantity_column], errors="coerce")
        invalid_mask = quantity_numeric < quantity_min

        if invalid_mask.any():
            issues[quantity_column] = {
                "rule": f"{quantity_column} must be >= {quantity_min}",
                "invalid_count": int(invalid_mask.sum()),
                "sample_rows": df[invalid_mask].head(5).to_dict(orient="records"),
            }

    price_column = rules.get("price_column")
    price_min = rules.get("price_min")

    if price_column and price_column in df.columns:
        price_numeric = pd.to_numeric(df[price_column], errors="coerce")
        invalid_mask = price_numeric <= price_min

        if invalid_mask.any():
            issues[price_column] = {
                "rule": f"{price_column} must be > {price_min}",
                "invalid_count": int(invalid_mask.sum()),
                "sample_rows": df[invalid_mask].head(5).to_dict(orient="records"),
            }

    date_column = rules.get("restocked_date_column")

    if date_column and date_column in df.columns:
        parsed_dates = pd.to_datetime(df[date_column], errors="coerce", dayfirst=True)
        future_mask = parsed_dates > pd.Timestamp.today()

        if future_mask.any():
            issues[date_column] = {
                "rule": f"{date_column} cannot be in the future",
                "invalid_count": int(future_mask.sum()),
                "sample_rows": df[future_mask].head(5).to_dict(orient="records"),
            }

    status = "PASS" if not issues else "FAIL"

    return {
        "check_name": "business_rule_validation",
        "dataset_name": dataset_name,
        "status": status,
        "issues": issues,
    }