
from perfLens.parsers.NEMO import Nemo
from perfLens.parserManager import register_parser

from utils.utils_files import *

import netCDF4 as nc

from functools import reduce
from operator import add
from pathlib import Path
import re

@register_parser
class NEMO5(Nemo):
    NEMO5_TIME_P_STEP = "timing_step.nc"
    PARSER_FILES = [Nemo.NEMO_TIMING, Nemo.NEMO_LAYOUT,
                    Nemo.NEMO_NAMELIST, Nemo.NEMO_TIMESTEP,
                    NEMO5_TIME_P_STEP]

    def __init__(self, rundir: Path):
        super().__init__(rundir)
        self.time_per_step_file = Path(self.rundir, self.NEMO5_TIME_P_STEP)


    def results_per_file(self):
        ret = super().results_per_file

        return ret

    @classmethod
    def parser_files(cls) -> list[str]:
        return super().parser_files() + [cls.PARSER_FILES]

    def avail_results(self) -> list[str]:
        ret = super().avail_results()
        if file_exists(self.timestep_file): ret += ["timesteps", "exec_stats"]
        if file_exists(self.lay_file): ret += ["layout"]
        if any([p for p in self.PARSER_FILES if p]): ret += ["main"]
        return ret

    def parse(self) -> None:
        super().parse()

        d_slurm  = self.env_data(self.env_file)
        # PERF DATA:
        d_ts     = self.exec_timesteps(self.timestep_file)
        d_elap_t = self.get_execution_time(self.timing_file)
        d_elap_ts= self.elap_time_from_ts(self.time_per_step_file, 0, -1)
        d_iter   = self.elap_time_from_ts(self.time_per_step_file, 3, -3)
        d_perf   =  d_ts | d_elap_t | d_elap_ts | d_iter
        # NM DATA:
        d_rl     = self.get_resolution_layout(self.lay_file)
        d_tile   = self.get_tiling_setup(self.namelist)
        d_ss     = self.sim_secs(self.namelist)
        d_jpnij  = self.jpni_jpnj(self.namelist)
        nm_data  = d_jpnij | d_rl | d_tile | d_ss

        # DERIVED DATA:
        #ts_x_s   = {"steps_per_sec" : None}
        #sim_days = None
        #sdpd     = {"sdpd": None}
        #sdpd_iter= {"sdpd_iter": None}

        #exec_stats = d_slurm | d_ts | d_perf | d_tile | ts_x_s | sdpd | sdpd_iter
        exec_stats = d_slurm | d_ts | d_perf | d_tile
        all_data = d_slurm | exec_stats | nm_data

        self._add_result("exec_stats", {"rundir": self.rundir} | exec_stats)
        self._add_result("nm_data", {"rundir": self.rundir} | nm_data)
        self._add_result("tiling", {"rundir": self.rundir} | d_tile)

        self._add_result("main", {"rundir": self.rundir} | all_data)


    @staticmethod
    def elap_time_from_ts(nc_time_for_step, from_ts=0, to_ts=-1) -> dict:
        try:
            data = nc.Dataset(nc_time_for_step, 'r')
            ts = data.variables["timing_step"][from_ts:to_ts]
            return {f"exec_time_{from_ts}_{to_ts}" : reduce(add, ts)}

        except Exception as e:
            return {f"exec_time_{from_ts}_{to_ts}" : None}

    @staticmethod
    def get_tiling_setup(nm_file : Path):
        tile_i = Nemo._nml_value(nm_file, "namtile", "nn_ltile_i", -1)
        tile_j = Nemo._nml_value(nm_file, "namtile", "nn_ltile_j", -1)
        return int(tile_i), int(tile_j)
