from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd

from perfLens.utils import matches


class Parser(ABC):
    """Extract results (tables) from the files found in a rundir.

    Subclasses set the mode `name` used in the CLI, the file `patterns`
    that identify a rundir, the `results` keys they produce, and implement
    `parse`.
    """
    name: str = ""
    patterns: List[str] = []
    results: List[str] = []

    def __init__(self, rundir: Union[str, Path]) -> None:
        self.rundir = Path(rundir)

    def files(self) -> List[Path]:
        """Files of the rundir handled by this parser."""
        if not self.rundir.is_dir():
            return []
        return sorted(f for f in self.rundir.iterdir()
                      if f.is_file() and matches(f.name, self.patterns))

    def available(self) -> List[str]:
        """Result keys that can be computed for this rundir."""
        return list(self.results) if self.files() else []

    @abstractmethod
    def parse(self) -> Dict[str, pd.DataFrame]:
        """Compute the results of the rundir, as {key: table}."""
