from pathlib import Path
from pprint import pprint

from utils.file_loader import load_csv
from utils.logger import setup_logger
from validation.data_profiler import generate_data_profile
from validation.schema_validator import validate_schema


SRC_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/source/warehouse_messy.csv")
TARGET_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/target/warehouse_messy.csv")


def main() -> None:
    setup_logger()

    source_df = load_csv(SRC_DATASET_PATH)
    target_df = load_csv(TARGET_DATASET_PATH)

    source_profile = generate_data_profile(
        df=source_df,
        dataset_name="source_warehouse",
        primary_key="Product ID",
    )

    target_profile = generate_data_profile(
        df=target_df,
        dataset_name="target_warehouse",
        primary_key="Product ID",
    )

    print("\nSOURCE DATA PROFILE")
    pprint(source_profile)

    print("\nTARGET DATA PROFILE")
    pprint(target_profile)

    schema_validation_results = validate_schema(source_df, target_df)
    print("\nSCHEMA VALIDATION RESULTS")
    pprint(schema_validation_results)

if __name__ == "__main__":
    main()