from .AbstractParser import AbstractParser
from pathlib import Path

class NEMO5(AbstractAnalyzer):

    def __init__(self, rundir: Path):
        super().__init__()
        self.rundir = rundir
        self.time_step_file = Path(self.rundir, "time.step")
        self.timing_file = Path(self.rundir, "timing.output")
        self.time_per_step_file = Path(self.rundir, "timing_step.nc")
        self.env_file = Path(self.rundir, "env.log")
        self.namelist = Path(self.rundir, "namelist_cfg")
        self.lay_file = Path(self.rundir, "layout.dat")

    @classmethod
    def analyzerFiles(cls):
        return super().analyzerFiles() + ["timing_step.nc","timing.output","env.log"]

    @classmethod
    def avail_results(cls):
        return []

    def get_results(self, results_key):
        return self.results[results_key]
