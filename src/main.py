from pathlib import Path
from pprint import pprint
from unittest import result

from src.utils.config_loader import load_yaml_config
from src.utils.file_loader import load_csv
from src.utils.logger import setup_logger

from src.settings import (VALIDATION_RULES_PATH,SOURCE_WAREHOUSE_DATASET_PATH,TARGET_WAREHOUSE_DATASET_PATH,WAREHOUSE_REPORT_PATH,)

from src.pandas_validation.data_profiler import generate_data_profile
from src.pandas_validation.structural_schema_validator import validate_schema
from src.pandas_validation.row_count_validator import validate_row_count_in_data
from src.pandas_validation.compeletness_validator import validate_completeness
from src.pandas_validation.uniquessness_data_validator import (validate_unique_data_without_duplicates,
)
from src.pandas_validation.validity_validator import validate_validity
from src.pandas_validation.business_rule_validator import validate_business_rules
from src.pandas_validation.parity_validator import validate_source_target_parity
from src.pandas_validation.report_generator import generate_json_report

def main() -> None:
    setup_logger()

    rules = load_yaml_config(VALIDATION_RULES_PATH)
    warehouse_rules = rules["warehouse_inventory"]

    source_df = load_csv(SOURCE_WAREHOUSE_DATASET_PATH)
    target_df = load_csv(TARGET_WAREHOUSE_DATASET_PATH)

    source_profile = generate_data_profile(
        df=source_df,
        dataset_name="source_warehouse",
        primary_key=warehouse_rules["primary_key"],
    )

    target_profile = generate_data_profile(
        df=target_df,
        dataset_name="target_warehouse",
        primary_key=warehouse_rules["primary_key"],
    )

    schema_result = validate_schema(source_df, target_df)

    row_count_result = validate_row_count_in_data(
        source_df=source_df,
        target_df=target_df,
    )

    source_completeness_result = validate_completeness(
        df=source_df,
        dataset_name="source_warehouse",
        required_columns=warehouse_rules["required_columns"],
        max_missing_percentage=warehouse_rules.get("max_missing_percentage", 0.0),
    )

    target_completeness_result = validate_completeness(
        df=target_df,
        dataset_name="target_warehouse",
        required_columns=warehouse_rules["required_columns"],
        max_missing_percentage=warehouse_rules.get("max_missing_percentage", 0.0),
    )

    source_uniqueness_result = validate_unique_data_without_duplicates(
        df=source_df,
        dataset_name="source_warehouse",
        primary_key=warehouse_rules["primary_key"],
    )

    target_uniqueness_result = validate_unique_data_without_duplicates(
        df=target_df,
        dataset_name="target_warehouse",
        primary_key=warehouse_rules["primary_key"],
    )

    source_validity_result = validate_validity(
        df=source_df,
        dataset_name="source_warehouse",
        rules=warehouse_rules,
    )

    target_validity_result = validate_validity(
        df=target_df,
        dataset_name="target_warehouse",
        rules=warehouse_rules,
    )

    source_business_rule_result = validate_business_rules(
        df=source_df,
        dataset_name="source_warehouse",
        rules=warehouse_rules["business_rules"],
    )

    target_business_rule_result = validate_business_rules(
        df=target_df,
        dataset_name="target_warehouse",
        rules=warehouse_rules["business_rules"],
    )

    parity_result = validate_source_target_parity(
        source_df=source_df,
        target_df=target_df,
        primary_key=warehouse_rules["primary_key"],
        compare_columns=warehouse_rules["compare_columns"],
    )

    validation_results = [
    #schema_validation_results,
    row_count_result,
    source_completeness_result,
    target_completeness_result,
    source_uniqueness_result,
    target_uniqueness_result,
    source_validity_result,
    target_validity_result,
    source_business_rule_result,
    target_business_rule_result,
    parity_result,
]

    generate_json_report(
    validation_results=validation_results,
    output_path=WAREHOUSE_REPORT_PATH,
)

    print("\nVALIDATION SUMMARY")

    for result in validation_results:
        print(
        f"{result.get('check_name', 'UNKNOWN_CHECK')} | "
        f"{result.get('dataset_name', 'N/A')} | "
        f"{result.get('status', 'UNKNOWN')}"
    )

    print(f"\nReport generated at: {WAREHOUSE_REPORT_PATH}")

    print("\nPARITY RESULT PREVIEW")
    pprint(parity_result)


if __name__ == "__main__":
    main()