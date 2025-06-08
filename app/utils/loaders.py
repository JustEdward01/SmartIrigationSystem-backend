import json
import logging
from pathlib import Path

PLANT_INFO_PATH = Path("plant_info.json")


def load_plant_info(plant_type: str | None = None) -> dict | None:
    """Load plant info from JSON file."""
    try:
        with PLANT_INFO_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if plant_type:
            return data.get(plant_type.lower())
        return data
    except Exception as exc:  # pragma: no cover - file reading errors
        logging.error("Error loading plant_info.json: %s", exc)
        return None
