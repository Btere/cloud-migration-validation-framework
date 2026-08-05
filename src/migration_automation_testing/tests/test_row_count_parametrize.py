import pandas as pd
import pytest
from src.pandas_validation.row_count_validator import validate_row_count_in_data

@pytest.mark.parametrize(
       "source_rows,target_rows,expected_difference,expected_status",
    [
        (3, 3, 0, "PASS"),
        (3, 4, 1, "FAIL"),
        (4, 3, -1, "FAIL"),
        (0, 0, 0, "PASS"),
    ],
)

def test_row_count_validation(source_rows, target_rows, expected_difference, expected_status):
    source_df = pd. DataFrame({"id": range(source_rows)})
    target_df = pd.DataFrame({"id": range(target_rows)})

    result = validate_row_count_in_data(source_df, target_df)

    assert result["source_count"] == source_rows
    assert result["target_count"] == target_rows
    assert result["difference"] == expected_difference
    assert result["status"] == expected_status
    