import logging
import pandas as pd
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from utils.file_loader import load_csv
from utils.logger import setup_logger

logger = logging.getLogger(__name__)


def generate_json_report(validation_results: List[Dict[str, Any]],output_path: Path,) -> None:
    """Generate a JSON validation evidence report.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "overall_status": (
            "PASS"
            if all(result.get("status") == "PASS" for result in validation_results)
            else "FAIL"
        ),
        "validation_results": validation_results,
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, default=str)