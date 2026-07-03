from pathlib import Path
from pprint import pprint
from unittest import result

from utils.config_loader import load_yaml_config
from utils.file_loader import load_csv
from utils.logger import setup_logger

from validation.data_profiler import generate_data_profile
from validation.structural_schema_validator import validate_schema
from validation.row_count_validator import validate_row_count_in_data
from validation.compeletness_validator import validate_completeness
from validation.uniquessness_data_validator import validate_unique_data_without_duplicates
from validation.validity_validator import validate_validity
from validation.business_rule_validator import validate_business_rules
from validation.parity_validator import validate_source_target_parity
from validation.report_generator import generate_json_report


VALIDATION_RULES_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/configs/validation_rules.yaml")

SOURCE_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/source/warehouse_messy.csv")

TARGET_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/target/warehouse_messy.csv")

REPORT_PATH = Path("reports/warehouse_validation_report.json")


def main() -> None:
    setup_logger()

    rules = load_yaml_config(VALIDATION_RULES_PATH)
    warehouse_rules = rules["warehouse_inventory"]

    source_df = load_csv(SOURCE_DATASET_PATH)
    target_df = load_csv(TARGET_DATASET_PATH)

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
    output_path=REPORT_PATH,
)

    print("\nVALIDATION SUMMARY")

    for result in validation_results:
        print(
        f"{result.get('check_name', 'UNKNOWN_CHECK')} | "
        f"{result.get('dataset_name', 'N/A')} | "
        f"{result.get('status', 'UNKNOWN')}"
    )

    print(f"\nReport generated at: {REPORT_PATH}")

    print("\nPARITY RESULT PREVIEW")
    pprint(parity_result)


if __name__ == "__main__":
    main()