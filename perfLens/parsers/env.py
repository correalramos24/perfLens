from pathlib import Path
from typing import Dict

import pandas as pd

from perfLens.parsers.base import Parser
from perfLens.utils import leading_int


class EnvParser(Parser):
    """SLURM job setup, from the environment dumped in env.log (`env > env.log`)."""
    name = "env"
    patterns = ["env.log"]
    results = ["slurm"]

    SLURM_VARS = {
        "nodes": "SLURM_NNODES",
        "mpi": "SLURM_TASKS_PER_NODE",
        "omp": "SLURM_CPUS_PER_TASK",
        "tasks": "SLURM_NTASKS",
    }

    def parse(self) -> Dict[str, pd.DataFrame]:
        rows = [self.slurm_setup(f) for f in self.files()]
        return {"slurm": pd.DataFrame(rows, columns=list(self.SLURM_VARS))}

    @classmethod
    def slurm_setup(cls, env_file: Path) -> Dict[str, int]:
        """SLURM setup of an env file; -1 for the missing values."""
        env = {}
        for line in env_file.read_text(errors="replace").splitlines():
            key, sep, value = line.partition("=")
            if sep:
                env[key] = value
        return {k: leading_int(env.get(var)) for k, var in cls.SLURM_VARS.items()}
