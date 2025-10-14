
from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser

from utils.utils_files import *
from utils.utils_slurm import get_slurm_env
from pathlib import Path

@register_parser
class EnvParser(AbstractParser):
    env_file_name = "env.log"

    def __init__(self, rundir: Path):
        super().__init__(rundir)
        self.env_file = Path(self.rundir, self.env_file_name)

    @classmethod
    def getParserFiles(cls):
        return super().getParserFiles() + [cls.env_file_name]

    def avail_results(self) -> list[str]:
        ret = []
        if file_exists(self.env_file): ret  += ["slurm_data"]
        return ret

    def parse(self) -> None:
        nodes, mpi, omp, tasks = get_slurm_env(self.env_file)
        self._add_result("slurm_data",{"rundir": self.rundir, "nodes": nodes,
            "mpi":mpi,"omp": omp,"tasks": tasks,
        })
