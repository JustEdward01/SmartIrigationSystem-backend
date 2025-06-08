"""Export logs from Supabase tables to CSV."""

import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

BACKUP_DIR = Path("backup")
BACKUP_DIR.mkdir(exist_ok=True)


def export_table(table: str, filename: str) -> None:
    """Export a Supabase table to CSV."""
    data = client.table(table).select("*").execute().data
    if not data:
        return
    with open(BACKUP_DIR / filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    """Export critical tables."""
    export_table("watering_logs", "watering_logs.csv")
    export_table("sensor_logs", "sensor_logs.csv")


if __name__ == "__main__":
    main()
