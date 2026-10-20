from typing import Dict, Type

from perfLens.parsers.base import Parser
from perfLens.parsers.env import EnvParser
from perfLens.parsers.mem import MemParser
from perfLens.parsers.pidstat import PidstatParser

# Available modes. To add a parser, subclass Parser and register it here.
PARSERS: Dict[str, Type[Parser]] = {
    p.name: p for p in (EnvParser, MemParser, PidstatParser)
}
