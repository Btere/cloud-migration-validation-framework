from pyspark.sql import SparkSession
from pathlib import Path
from pprint import pprint
from src.pyspark_validation.data_profiler import generate_data_profile
from src.pyspark_validation.schema_validator import validate_schema
from src.pyspark_validation.row_count_validator import validate_row_count

from src.settings import (VALIDATION_RULES_PATH,SOURCE_WAREHOUSE_DATASET_PATH,TARGET_WAREHOUSE_DATASET_PATH,WAREHOUSE_REPORT_PATH,)
from src.settings import VALIDATION_RULES_PATH
from src.utils.config_loader import load_yaml_config
from src.pyspark_validation.completeness_validator import (validate_completeness,)


def main() -> None:
    spark = (SparkSession.builder
        .appName("cloud-migration-data-profiling")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        source_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(SOURCE_WAREHOUSE_DATASET_PATH))
        )

        target_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(TARGET_WAREHOUSE_DATASET_PATH))
        )
        rules = load_yaml_config(VALIDATION_RULES_PATH)
        warehouse_rules = rules["warehouse_inventory"]
        
        source_profile = generate_data_profile(df=source_df,dataset_name="source_warehouse",primary_key="Product ID",)

        target_profile = generate_data_profile(df=target_df,dataset_name="target_warehouse",primary_key="Product ID",)

        #print("\nSOURCE PYSPARK PROFILE")
        #pprint(source_profile)

        #print("\nTARGET PYSPARK PROFILE")
        #pprint(target_profile)
        schema_result = validate_schema(
        source_df=source_df,
        target_df=target_df,
        check_column_order=True,
        check_nullability=False,)

        #print("\nPYSPARK SCHEMA VALIDATION RESULT")
        #pprint(schema_result)
        
        row_count_result = validate_row_count(
        source_df=source_df,
        target_df=target_df,
)

        #print("\nPYSPARK ROW COUNT VALIDATION RESULT")
        #pprint(row_count_result)
        

    finally:
        spark.stop()
        
  


if __name__ == "__main__":
    main()