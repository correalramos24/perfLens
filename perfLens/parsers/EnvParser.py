
from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser

from py_utils.utils_files import file_exists
from py_utils.slurm import SlurmDirectives
from pathlib import Path
import re

@register_parser
class EnvParser(AbstractParser):
    env_file_name = "env.log"

    def __init__(self, rundir: Path):
        super().__init__(rundir)
        self.env_file = Path(self.rundir, self.env_file_name)

    @classmethod
    def parser_files(cls) -> list[str]:
        return super().parser_files() + [cls.env_file_name]

    def avail_results(self) -> list[str]:
        ret = []
        if file_exists(self.env_file): ret.append("slurm_data")
        return ret

    def parse(self) -> None:
        d = self._parse_env_data(self.env_file)
        self._add_result("slurm_data",{"rundir": self.rundir} | d)

    @staticmethod
    def _parse_env_data(env_file : Path) -> dict:
        dirs = SlurmDirectives.from_env_file(env_file)
        return {k: EnvParser._leading_int(getattr(dirs, k))
                for k in ("nodes", "mpi", "omp", "tasks")}

    @staticmethod
    def _leading_int(value: str | None) -> int:
        """Parse SLURM values like '110(x8)' -> 110, missing -> -1"""
        m = re.match(r"\d+", value) if value else None
        return int(m.group()) if m else -1
        