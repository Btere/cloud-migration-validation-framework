import logging
import pytest
import pandas as pd
from pathlib import Path
from typing import Any, Dict
from pyspark.sql import DataFrame
from src.migration_automation_testing.pytest_concept. pytest_decorator import log_test

logging.basicConfig(level=logging.INFO)
project_root = Path(__file__).resolve().parents[2]

@pytest.fixture(scope="module")

def review_dataset():
   """Load the source and target review datasets once
    and make them available to all tests.
    """

    source_file = (project_root/ "dataset"/ "source"/ "source_reviews.csv")

    target_file = (project_root/ "dataset"/ "target"/ "target_reviews.csv")

    source_df = pd.read_csv(source_file)
    target_df = pd.read_csv(target_file)

    print("\nSetup: Loaded review datasets")

    yield source_df, target_df

    print("\nTeardown: Cleaning up") 