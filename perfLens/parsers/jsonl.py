import json
from pathlib import Path
from typing import Dict

import pandas as pd

from perfLens.parsers.base import Parser
from perfLens.utils import logger


class JsonlParser(Parser):
    """Records from JSON Lines files (*.jsonl, one JSON object per line)."""
    name = "jsonl"
    patterns = ["*.jsonl", "*.ndjson"]
    results = ["records"]

    def parse(self) -> Dict[str, pd.DataFrame]:
        tables = [self.read_jsonl(f) for f in self.files()]
        return {"records": pd.concat(tables, ignore_index=True, sort=False)}

    @staticmethod
    def read_jsonl(jsonl_file: Path) -> pd.DataFrame:
        """Table with one row per object. Nested objects are flattened into
        dotted columns ({"mem": {"rss": 1}} -> mem.rss); invalid lines are
        skipped with a warning."""
        records = []
        for n, line in enumerate(jsonl_file.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError as e:
                logger.warning("%s:%d: skipping invalid JSON (%s)", jsonl_file, n, e)
                continue
            if not isinstance(record, dict):
                logger.warning("%s:%d: skipping, not a JSON object", jsonl_file, n)
                continue
            records.append(record)

        df = pd.json_normalize(records) if records else pd.DataFrame()
        df.insert(0, "file", jsonl_file.name)
        return df
