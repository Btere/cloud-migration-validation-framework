import pandas as pd

from pathlib import Path
from typing import Dict, List, Union

SRC_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/source/warehouse_messy.csv")
TARGET_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/target/warehouse_clean.csv")

def load_dataset(path: Path) -> pd.DataFrame:
    """ Load a dataset from a CSV file.

    Args: path (Path): The path to the CSV file.
    Returns: pd.DataFrame: The loaded dataset as a pandas DataFrame.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected CSV file, got: {path.suffix}")
    return pd.read_csv(path)