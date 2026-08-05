import logging
import pytest
from pyspark.sql import SparkSession



@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("migration-validation")
        .getOrCreate()
    )

    yield session

    session.stop()