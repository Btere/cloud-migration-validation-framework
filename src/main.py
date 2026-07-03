from pathlib import Path
from pprint import pprint

from utils.file_loader import load_csv
from utils.logger import setup_logger
from validation.data_profiler import generate_data_profile
from validation.structural_schema_validator import validate_schema
from validation.row_count_validator import validate_row_count_in_data
from validation.compeletness_validator import validate_completeness
from utils.config_loader import load_yaml_config



VALIDATION_RULES_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/configs/validation_rules.yaml")
SRC_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/source/warehouse_messy.csv")
TARGET_DATASET_PATH = Path("/Users/btereomotere/Downloads/Small Object dataset/data-migration-quality-check/cloud-migration-validation-framework/dataset/target/warehouse_messy.csv")


def main() -> None:
    setup_logger()

    source_df = load_csv(SRC_DATASET_PATH)
    target_df = load_csv(TARGET_DATASET_PATH)

    source_profile = generate_data_profile(df=source_df, dataset_name="source_warehouse", primary_key="Product ID",)

    target_profile = generate_data_profile(df=target_df, dataset_name="target_warehouse",primary_key="Product ID",)

    #print("\nSOURCE DATA PROFILE")
    #pprint(source_profile)

    #print("\nTARGET DATA PROFILE")
    #pprint(target_profile)
    schema_validation_results = validate_schema(source_df, target_df)
    #print("\nSCHEMA VALIDATION RESULTS")
    #pprint(schema_validation_results)
    
    rules = load_yaml_config(VALIDATION_RULES_PATH)
    warehouse_rules = rules["warehouse_inventory"]
    
    source_completeness_results = validate_completeness(
        df=source_df,
        dataset_name="source_warehouse",
        required_columns=warehouse_rules["required_columns"],
        max_missing_percentage=warehouse_rules.get("max_missing_percentage", 0.0)
        #max_missing_percentage=warehouse_rules["max_missing_percentage"],
    )
    
    print("\nSOURCE COMPLETENESS VALIDATION RESULTS")
    pprint(source_completeness_results)
    
    

if __name__ == "__main__":
    main()