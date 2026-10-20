"""Find the rundirs, run the parsers and merge their results."""
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import pandas as pd

from perfLens.parsers import PARSERS, Parser
from perfLens.utils import find_dirs, logger

PathLike = Union[str, Path]


def get_parsers(mode: str, inputs: Iterable[PathLike],
                explore: bool = False) -> List[Parser]:
    """A parser for each rundir. With explore, the inputs are searched
    recursively for rundirs containing files of the selected mode."""
    if mode not in PARSERS:
        raise ValueError(f"Unknown mode '{mode}', use one of: {', '.join(PARSERS)}")
    parser_cls = PARSERS[mode]
    rundirs: List[Path] = []
    for path in map(Path, inputs):
        if not path.is_dir():
            logger.warning("Skipping %s: not a directory", path)
        elif explore:
            rundirs += find_dirs(path, parser_cls.patterns)
        else:
            rundirs.append(path)
    return [parser_cls(r) for r in rundirs]


def gather(parsers: Iterable[Parser]) -> Dict[str, pd.DataFrame]:
    """Parse every rundir and merge the results with the same key into one
    table, adding a `rundir` column."""
    tables: Dict[str, List[pd.DataFrame]] = {}
    for p in parsers:
        if not p.files():
            logger.warning("No %s files found in %s", "/".join(p.patterns), p.rundir)
            continue
        logger.debug("Parsing %s", p.rundir)
        try:
            results = p.parse()
        except Exception as e:  # keep going with the other rundirs
            logger.error("Unable to parse %s: %s", p.rundir, e)
            continue
        for key, df in results.items():
            df.insert(0, "rundir", str(p.rundir))
            tables.setdefault(key, []).append(df)
    return {k: pd.concat(v, ignore_index=True, sort=False) for k, v in tables.items()}


def collect(mode: str, inputs: Iterable[PathLike],
            explore: bool = False) -> Dict[str, pd.DataFrame]:
    """Results of the given mode for the inputs, as {key: table}.

    >>> collect("mem", ["inputs"], explore=True)["mem"]
    """
    return gather(get_parsers(mode, inputs, explore))


def select(df: pd.DataFrame, cols: Optional[List[str]] = None,
           sort: Optional[List[str]] = None, desc: bool = False) -> pd.DataFrame:
    """Keep only the given columns (if any) and sort by the given ones."""
    if cols:
        missing = [c for c in cols if c not in df.columns]
        if missing:
            logger.warning("Unknown column(s) %s, available: %s",
                           ", ".join(missing), ", ".join(df.columns))
        df = df[[c for c in cols if c in df.columns]]
    if sort:
        by = [c for c in sort if c in df.columns]
        if len(by) != len(sort):
            logger.warning("Unable to sort by unknown column(s): %s",
                           ", ".join(c for c in sort if c not in df.columns))
        if by:
            df = df.sort_values(by, ascending=not desc)
    return df
