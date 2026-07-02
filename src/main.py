import pandas as pd

from pathlib import Path
from typing import Dict, List, Union
from validation.data_loader import load_dataset, SRC_DATASET_PATH, TARGET_DATASET_PATH


if __name__ == "__main__":
    # Load the source and target datasets
    source_df = load_dataset(SRC_DATASET_PATH)
    target_df = load_dataset(TARGET_DATASET_PATH)

    # Display the first few rows of each dataset
    print("Source Dataset:")
    print(source_df.head())
    print("\nTarget Dataset:")
    print(target_df.head())