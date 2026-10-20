import re
from pathlib import Path
from typing import Dict, List

import pandas as pd

from perfLens.parsers.base import Parser


class PidstatParser(Parser):
    """Per-process CPU usage from pidstat logs (e.g. `pidstat 1 > run.pstat`)."""
    name = "pidstat"
    patterns = ["*.pstat"]
    results = ["cpu"]

    # Timestamp (12h clocks add AM/PM) followed by the rest of the line
    LINE_RE = re.compile(r"^(\S+(?: [AP]M)?)\s+(\S.*)$")

    def parse(self) -> Dict[str, pd.DataFrame]:
        tables = [self.read_pidstat(f) for f in self.files()]
        return {"cpu": pd.concat(tables, ignore_index=True, sort=False)}

    @classmethod
    def read_pidstat(cls, pstat_file: Path) -> pd.DataFrame:
        """Table with one row per process and sample. The columns are taken
        from the pidstat header, so different pidstat versions are supported."""
        header: List[str] = []
        rows = []
        for line in pstat_file.read_text().splitlines():
            if line.startswith("Average:"):
                break
            m = cls.LINE_RE.match(line)
            if not m:
                continue
            timestamp, rest = m.groups()
            fields = rest.split()
            if fields[-1] == "Command":
                header = fields
            elif header:
                rows.append([timestamp] + rest.split(None, len(header) - 1))

        df = pd.DataFrame(rows, columns=["time"] + header)
        for col in header[:-1]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.insert(0, "file", pstat_file.name)
        return df
