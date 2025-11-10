
from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser

from utils.utils_files import *
from utils.utils_slurm import slurm_env
from pathlib import Path

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
        return slurm_env(env_file)._asdict()
        