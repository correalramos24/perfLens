
from perfLens.parsers.EnvParser import EnvParser
from perfLens.parserManager import register_parser

from utils.utils_files import *

import netCDF4 as nc

from functools import reduce
from operator import add
from pathlib import Path
import re

@register_parser
class NEMO5(EnvParser):

    NEMO5_TIMING        = "timing.output"
    NEMO5_LAYOUT        = "layout.dat"
    NEMO5_NAMELIST      = "namelist_cfg"
    NEMO5_TIMESTEP      = "time.step"
    NEMO5_TIME_P_STEP   = "timing_step.nc"
    PARSER_FILES = [NEMO5_TIMING, NEMO5_LAYOUT, NEMO5_NAMELIST,
                    NEMO5_TIMESTEP, NEMO5_TIME_P_STEP]

    def __init__(self, rundir: Path):
        super().__init__(rundir)
        self.rundir = rundir
        self.time_step_file = Path(self.rundir, self.NEMO5_TIMESTEP)
        self.timing_file = Path(self.rundir, self.NEMO5_TIMING)
        self.time_per_step_file = Path(self.rundir, self.NEMO5_TIME_P_STEP)
        self.namelist = Path(self.rundir, self.NEMO5_NAMELIST)
        self.lay_file = Path(self.rundir, self.NEMO5_LAYOUT)

    @classmethod
    def getParserFiles(cls) -> list[str]:
        return super().getParserFiles() + [cls.PARSER_FILES]
    
    def avail_results(self) -> list[str]:
        ret = super().avail_results()
        
        if file_exists(self.time_step_file): ret += ["timesteps", "exec_stats"]
        if file_exists(self.lay_file): ret += ["layout"]
        if any([p for p in self.PARSER_FILES if p]): ret += ["main"]
        return ret

    def parse(self) -> None:
        super().parse()
        
        d_slurm  = self.get_env_data(self.env_file)
        # PERF DATA:
        d_ts     = self.get_timesteps(self.time_step_file)
        d_elap_t = self.get_execution_time(self.timing_file)
        d_elap_ts= self.elap_time_from_ts(self.time_per_step_file, 0, -1)
        d_iter   = self.elap_time_from_ts(self.time_per_step_file, 3, -3)
        d_perf   =  d_ts | d_elap_t | d_elap_ts | d_iter
        # NM DATA:
        d_rl     = self.get_resolution_layout(self.lay_file)
        d_tile   = self.get_tiling_setup(self.namelist)
        d_ss     = self.get_sim_secs(self.namelist)
        d_jpnij  = self.get_jpni_jpnj(self.namelist)
        nm_data  = d_jpnij | d_rl | d_tile | d_ss
        
        # DERIVED DATA:
        ts_x_s   = {"steps_per_sec" : None}
        sim_days = None
        sdpd     = {"sdpd": None}
        sdpd_iter= {"sdpd_iter": None}
        
        exec_stats = d_ts | d_perf | d_tile | ts_x_s | sdpd | sdpd_iter
        all_data = d_slurm | exec_stats | nm_data
        
        self._add_result("exec_stats", {"rundir": self.rundir} | exec_stats)
        self._add_result("nm_data", {"rundir": self.rundir} | nm_data)
        self._add_result("tiling", {"rundir": self.rundir} | d_tile)
        
        self._add_result("main", {"rundir": self.rundir} | all_data)
    
    @staticmethod
    def get_timesteps(timestep_file : Path) -> dict:
        try:
            with open(timestep_file) as file:
                lines = file.readlines()
                if lines: 
                    return {"ts": int(lines[-1].strip())}        
        except Exception as e:
            print("EXCEPTION:", e)
        return {"ts": None}
    
    @staticmethod
    def get_execution_time(timing_file: Path) -> dict:
        """Parse total execution time from timing.output"""
        try:
            with open(timing_file) as file:
                for line in file.readlines():
                    match = re.search(r"max over all MPI processes = ([\d.]+)s", line)
                    if match:
                        return {"exec_time" : float(match.group(1))}
        except Exception as e:
            print(e)
            pass
        return {"exec_time": None}
    
    @staticmethod
    def elap_time_from_ts(nc_time_for_step, from_ts=0, to_ts=-1) -> dict:
        try:
            data = nc.Dataset(nc_time_for_step, 'r')
            ts = data.variables["timing_step"][from_ts:to_ts]
            return {f"exec_time_{from_ts}_{to_ts}" : reduce(add, ts)} 

        except Exception as e:
            return {f"exec_time_{from_ts}_{to_ts}" : None}

    @staticmethod
    def get_sim_secs(nm_file : Path) -> dict:
        try:
            import f90nml
            nml = f90nml.read(nm_file)
            return {"sim_secs" : int(nml["namdom"]["rn_Dt"])}
        except Exception as e:
            return {"sim_secs", None}
  
    @staticmethod
    def get_jpni_jpnj(nm_file : Path) -> dict:
        try:
            import f90nml
            nml = f90nml.read(nm_file)
            return {"jpni": nml["nammpp"]["jpni"], 
                    "jpnj": nml["nammpp"]["jpnj"]}
        except Exception as e:
            return {"jpni": None, "jpnj" : None}
    
    @staticmethod
    def get_tiling_setup(nm_file : Path):
        ret = {}
        try:
            import f90nml
            nml = f90nml.read(nm_file)
            if nml["namtile"]["ln_tile"]:
                ret["tiling_i"] = nml["namtile"]["nn_ltile_i"]
                ret["tiling_j"] = nml["namtile"]["nn_ltile_j"]
        except Exception as e:
            pass
        return ret
   
    @staticmethod
    def get_resolution_layout(layout_file : Path) -> dict:
        try:
            with open(layout_file) as f:
                data = f.readlines()
            values = data[2].split("(")[0].split()
            return {
                "jpimax":  int(values[1]),"jpjmax": int(values[2]),
                "jpk":     int(values[3]),
                "jpiglo":  int(values[4]),"jpjglo": int(values[5])
            }
        except Exception as e:
            return {
                "jpimax":None,"jpjmax":None,
                "jpk":None,"jpiglo":None,"jpjglo":None
            } 
    
    