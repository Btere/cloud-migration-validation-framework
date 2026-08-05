import logging
import pandas as pd

from src.pandas_validation.data_profiler import generate_data_profile

logging.basicConfig(level=logging.INFO)

def test_generate_basic_profile():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Abu", "Tola", "Ada"],
            "score": [85.5, 90.0, 78.5],
        }
    )

    profile = generate_data_profile(
        df=df,
        dataset_name="students",
        primary_key="id",
    )

    assert profile["dataset_name"] == "students"
    assert profile["row_count"] == 3
    assert profile["column_count"] == 3
    assert profile["columns"] == ["id", "name", "score"]
    assert profile["missing_values"] == {
        "id": 0,
        "name": 0,
        "score": 0,
    }
    assert profile["duplicate_row_count"] == 0
    assert profile["duplicate_primary_key_count"] == 0
    assert profile["unique_values_per_column"]["name"] == 3


def test_detects_missing_values_and_percentages():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "name": ["Abu", None, "Ada", None],
        }
    )

    profile = generate_data_profile(df, "customers")

    assert profile["missing_values"]["name"] == 2
    assert profile["missing_percentage"]["name"] == 50.0
    assert profile["missing_values"]["id"] == 0


def test_detects_duplicate_rows_and_primary_keys():
    df = pd.DataFrame(
        {
            "id": [1, 2, 2, 2],
            "name": [
                "Abu",
                "Tola",
                "Tola",
                "Different name",
            ],
        }
    )

    profile = generate_data_profile(
        df=df,
        dataset_name="customers",
        primary_key="id",
    )

    assert profile["duplicate_row_count"] == 1
    assert len(profile["duplicate_rows_preview"]) == 1

    assert profile["duplicate_primary_key_count"] == 2
    assert len(profile["duplicate_primary_key_preview"]) == 3


def test_missing_primary_key_is_reported(caplog):
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Abu", "Ada"],
        }
    )

    with caplog.at_level(logging.WARNING):
        profile = generate_data_profile(
            df=df,
            dataset_name="customers",
            primary_key="customer_id",
        )

    assert profile["primary_key"] == "customer_id"
    assert profile["primary_key_found"] is False
    assert "Primary key 'customer_id' not found" in caplog.text