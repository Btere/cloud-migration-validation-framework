from pyspark.sql import SparkSession
from pathlib import Path
from pprint import pprint
from src.pyspark_validation.data_profiler import generate_data_profile

from src.settings import (VALIDATION_RULES_PATH,SOURCE_WAREHOUSE_DATASET_PATH,TARGET_WAREHOUSE_DATASET_PATH,WAREHOUSE_REPORT_PATH,)


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

        source_profile = generate_data_profile(df=source_df,dataset_name="source_warehouse",primary_key="Product ID",)

        target_profile = generate_data_profile(df=target_df,dataset_name="target_warehouse",primary_key="Product ID",)

        print("\nSOURCE PYSPARK PROFILE")
        pprint(source_profile)

        print("\nTARGET PYSPARK PROFILE")
        pprint(target_profile)

    finally:
        spark.stop()
        
  


if __name__ == "__main__":
    main()