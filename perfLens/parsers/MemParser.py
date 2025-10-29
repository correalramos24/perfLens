import numpy as np

from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser
from utils.utils_py import to_int_list
import pandas as pd
from pathlib import Path

@register_parser
class MemParser(AbstractParser):

    MEM_INFO = ["timing", "total", "used","free", "shared", "buff/cache", "available"]
    SWP_INFO = ["total_swap", "used_swap", "free_swap"]
    def __init__(self, rundir: Path) -> None:
        super().__init__(rundir)
        self.mem_files = list(rundir.glob("*.mem"))
        self.mem_files_names = [f.name for f in self.mem_files]

    @classmethod
    def getParserWildcards(cls) -> list[str]:
        return super().getParserWildcards() + ["*.mem"]

    def avail_results(self) -> list[str]:
        ret = self.mem_files_names.copy()
        if ret: ret += ["mem-data"]
        return ret

    def parse(self) -> None:
        super().parse()
        for f in self.mem_files:
            self._dbg("Parsing", f.name)
            self._add_result(str(f.name), self.get_mem_data(f))
        if self.mem_files:
            self._add_result("mem-data", self.__join_mem_data())

    @staticmethod
    def get_mem_data(fpath: Path, samp_time: int = 1, swap: bool = False,
                     scale_factor: int = 1024 * 1024) -> pd.DataFrame:
        data, timing = [], 0
        with open(fpath, mode='r') as mem_file:
            for line in mem_file.readlines():
                if "Mem: " in line:
                    data.append([timing] + to_int_list(line.split()[1:]))
                    timing += samp_time
                if swap and "Swap: " in line:
                    data[-1].extend(to_int_list(line.split()[1:]))

        cols = MemParser.MEM_INFO if not swap else MemParser.MEM_INFO + MemParser.SWP_INFO
        df = pd.DataFrame(columns=cols, data=data)
        df["host"] = fpath.name.replace(".mem", "")

        not_timing = df.columns.difference(["timing", "host", "used_perc"])
        df[not_timing] = df[not_timing].apply(lambda x: x / scale_factor)
        df[not_timing] = df[not_timing].round(2)

        df["used_perc"] = (df["used"] / df["total"]) * 100
        if swap: df["used_swap_perc"] = (df["used_swap"] / df["total_swap"]) * 100

        return df

    def __join_mem_data(self) -> pd.DataFrame:
        df_list = [self.get_results(f) for f in self.mem_files_names]
        return pd.concat(df_list, ignore_index=True)