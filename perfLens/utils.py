"""Small helpers shared across perfLens."""
import fnmatch
import logging
import os
import re
from pathlib import Path
from typing import Iterable, List, Optional, Union

logger = logging.getLogger("perfLens")


def setup_logging(level: int = logging.INFO) -> None:
    """Print perfLens messages to stderr, keeping stdout for the results."""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
    logger.handlers = [handler]
    logger.setLevel(level)
    logger.propagate = False


def matches(file_name: str, patterns: Iterable[str]) -> bool:
    """True if file_name matches any of the (glob) patterns."""
    return any(fnmatch.fnmatch(file_name, p) for p in patterns)


def find_dirs(root: Union[str, Path], patterns: Iterable[str]) -> List[Path]:
    """Folders under root (root included) containing a file that matches
    any of the patterns."""
    patterns = list(patterns)
    return sorted(Path(dirpath) for dirpath, _, fnames in os.walk(str(root))
                  if any(matches(f, patterns) for f in fnames))


def leading_int(value: Optional[str], default: int = -1) -> int:
    """Parse the leading integer of value, e.g. '110(x8)' -> 110."""
    m = re.match(r"\s*(\d+)", value) if value else None
    return int(m.group(1)) if m else default
