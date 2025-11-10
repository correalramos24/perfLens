from perfLens.parsers.EnvParser import EnvParser
from perfLens.parserManager import register_parser

from utils.utils_files import *

import netCDF4 as nc

from functools import reduce
from operator import add
from pathlib import Path
import re

try:
    import f90nml
except ImportError:
    f90nml = None
    MyLogger.warning("Unable to find f90nml package!")

@register_parser
class Nemo(EnvParser):
    NEMO_TIMESTEP = "time.step"
    NEMO_TIMING = "timing.output"
    NEMO_LAYOUT = "layout.dat"
    NEMO_NAMELIST = "namelist_cfg"

    def __init__(self, rundir: Path):
        super().__init__(rundir)

        self.rundir = rundir
        self.timestep_file = Path(self.rundir, self.NEMO_TIMESTEP)
        self.timing_file = Path(self.rundir, self.NEMO_TIMING)
        self.namelist = Path(self.rundir, self.NEMO_NAMELIST)
        self.lay_file = Path(self.rundir, self.NEMO_LAYOUT)

    @property
    def results_per_file(self):
        return {}

    # EXEC TIME:
    @staticmethod
    def exec_time(timing_file: Path) -> float:
        if not file_exists(timing_file):
            MyLogger.warning(f"Unable to find {Nemo.NEMO_TIMING} file @ {timing_file}")
            return float(-1)
        with open(timing_file) as file:
            for line in file.readlines():
                match = re.search(r'max over all MPI processes = ([\d.]+)s', line)
                if match:
                    return float(match.group(1))
        return float(-1)

    # TIMESTEPS:
    @staticmethod
    def exec_timesteps(timestep_file : Path) -> int:
        if not file_exists(timestep_file):
            MyLogger.warning(f"Unable to find timestep file @ {timestep_file}")
            return -1
        with open(timestep_file) as file:
            *_, last = file
            return int(last)

    # RESOLUTION:
    @staticmethod
    def resolution_layout(layout_file : Path) -> tuple[int, int, int, int, int]:
        if not file_exists(layout_file):
            MyLogger.warning(f"Unable to find {Nemo.NEMO_LAYOUT} file @ {layout_file}")
            return -1,-1,-1,-1,-1
        with open(layout_file) as f:
            data = f.readlines()
            values = data[2].split("(")[0].split()
            return int(values[1]), int(values[2]), int(values[3]),int(values[4]),int(values[5])

    # NAMELIST DATA:
    @staticmethod
    def sim_timesteps(nm_file: Path) -> int | None:
        sim_ts = Nemo._nml_value(nm_file, "namrun", "nn_itend")
        return int(sim_ts) if sim_ts else None

    @staticmethod
    def sim_secs(nm_file : Path) -> int | None:
        sim_secs = Nemo._nml_value(nm_file, "namdom", "rn_Dt")
        return int(sim_secs) if sim_secs else None

    @staticmethod
    def jpni_jpnj(nm_file: Path) -> tuple[int, int]:
        jpni = Nemo._nml_value(nm_file, "nammpp", "jpni", -1)
        jpnj = Nemo._nml_value(nm_file, "nammpp", "jpnj", -1)
        return int(jpni), int(jpnj)

    # ==============================PRIVATE METHODS=====================================
    @staticmethod
    def _nml_value(nm_file: Path, nmlist: str, param: str, default = None) -> str:
        if f90nml is None:
            return default
        nml = f90nml.read(nm_file)
        if nmlist in nml:
            nmlist =  nml[nmlist]
            if param in nmlist:
                return nmlist[param]
        return default

    @staticmethod
    def _nml_value_exception(nm_file: Path, nmlist: str, param: str):
        if f90nml is None: raise Exception("f90nml not found")
        nml = f90nml.read(nm_file)
        return nml[nmlist][param]