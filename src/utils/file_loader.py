from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def load_csv(path: Path) -> pd.DataFrame:
    """
    Load a CSV dataset after basic file validation.

    Args:
        path: Path to the CSV file.

    Returns:
        A pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the path is not a file, not a CSV, or the CSV is empty.
        RuntimeError: If pandas fails to load the file.
    """
    logger.info("Loading CSV file: %s", path)

    if not path.exists():
        logger.error("File not found: %s", path)
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        logger.error("Path is not a file: %s", path)
        raise ValueError(f"Path is not a file: {path}")

    if path.suffix.lower() != ".csv":
        logger.error("Invalid file type: %s", path.suffix)
        raise ValueError(f"Expected CSV file, got: {path.suffix}")

    try:
        df = pd.read_csv(path)
        logger.info(
            "Loaded CSV successfully: %s | rows=%s | columns=%s",
            path.name,
            df.shape[0],
            df.shape[1],
        )
        return df

    except pd.errors.EmptyDataError as exc:
        logger.error("CSV file is empty: %s", path)
        raise ValueError(f"CSV file is empty: {path}") from exc

    except Exception as exc:
        logger.exception("Failed to load CSV file: %s", path)
        raise RuntimeError(f"Failed to load CSV file: {path}") from exc