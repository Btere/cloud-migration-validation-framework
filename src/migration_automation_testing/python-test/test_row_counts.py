import pandas as pd
from src.pandas_validation.row_count_validator import validate_row_count_in_data

def test_row_count_match():
    source_df = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})
    target_df = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "", "Charlie"]})
    result = validate_row_count_in_data(source_df, target_df)
    assert result["status"] == "PASS"
    assert result["difference"] == 0
    
def test_target_has_more_rows():
    source_df = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})
    target_df = pd.DataFrame({"id": [1, 2, 3, 4], "name": ["Alice", "Bob", "Charlie", "David"]})
    result = validate_row_count_in_data(source_df, target_df)
    assert result["status"] == "FAIL"
    assert result["difference"] == 1
    assert result["target_count"] == 4


def test_source_has_more_rows():
    source_df = pd.DataFrame({"id": [1, 2, 3, 4], "name": ["Alice", "Bob", "Charlie", "David"]})
    target_df = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})
    result = validate_row_count_in_data(source_df, target_df)
    assert result["status"] == "FAIL"
    assert result["difference"] == -1
    assert result["source_count"] == 4
    
def test_empty_dataframes():
    source_df = pd.DataFrame()

    target_df = pd.DataFrame()

    result = validate_row_count_in_data(source_df, target_df)

    assert result["source_count"] == 0
    assert result["target_count"] == 0
    assert result["difference"] == 0
    assert result["status"] == "PASS"
    
def test_large_dataset():
    source_df = pd.DataFrame(
        {
            "id": range(10000)
        }
    )

    target_df = pd.DataFrame(
        {
            "id": range(10000)
        }
    )

    result = validate_row_count_in_data(source_df, target_df)

    assert result["source_count"] == 10000
    assert result["target_count"] == 10000
    assert result["difference"] == 0
    assert result["status"] == "PASS"
    
    