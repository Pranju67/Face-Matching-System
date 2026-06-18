"""
FaceMatch Pro - Utilities
"""

import csv
import os
import datetime
from typing import List, Dict


def export_csv(records: List[Dict], path: str) -> str:
    """Export history records to a CSV file. Returns the path."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    fields = ["_id", "image1_name", "image2_name", "similarity_score",
              "match_status", "processing_time", "timestamp"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            row = dict(rec)
            if isinstance(row.get("timestamp"), datetime.datetime):
                row["timestamp"] = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(row)
    return path


def format_timestamp(ts) -> str:
    if isinstance(ts, datetime.datetime):
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    return str(ts) if ts else ""


def short_filename(path: str, max_len: int = 28) -> str:
    name = os.path.basename(path)
    if len(name) > max_len:
        return name[:max_len-3] + "..."
    return name


def score_color(score: float) -> str:
    """Return a hex colour appropriate for the score value."""
    if score >= 75:
        return "#10B981"   # green
    if score >= 60:
        return "#F59E0B"   # amber
    return "#EF4444"       # red


def make_report_id() -> str:
    return datetime.datetime.now().strftime("RPT-%Y%m%d-%H%M%S")
