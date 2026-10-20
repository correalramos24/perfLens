from pathlib import Path
from typing import Dict

import pandas as pd

from perfLens.parsers.base import Parser


class MemParser(Parser):
    """Memory usage sampled with `free` into <host>.mem files
    (e.g. `free -s 1 > $(hostname).mem`)."""
    name = "mem"
    patterns = ["*.mem"]
    results = ["mem"]

    COLUMNS = ["total", "used", "free", "shared", "buff/cache", "available"]

    def parse(self) -> Dict[str, pd.DataFrame]:
        tables = [self.read_free(f) for f in self.files()]
        return {"mem": pd.concat(tables, ignore_index=True)}

    @classmethod
    def read_free(cls, mem_file: Path, samp_time: float = 1,
                  scale: int = 1024 * 1024) -> pd.DataFrame:
        """Table with one row per sample. `free` reports KiB, the default
        scale converts them to GiB."""
        rows = [line.split()[1:len(cls.COLUMNS) + 1]
                for line in mem_file.read_text().splitlines()
                if line.startswith("Mem:")]
        df = (pd.DataFrame(rows, columns=cls.COLUMNS).astype(float) / scale).round(2)
        df["used_perc"] = (df["used"] / df["total"] * 100).round(2)
        df.insert(0, "time", [i * samp_time for i in range(len(df))])
        df.insert(0, "host", mem_file.stem)
        return df
