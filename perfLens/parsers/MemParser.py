
from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser

import pandas as pd
from pathlib import Path

@register_parser
class MemParser(AbstractParser):
    def __init__(self, rundir: Path) -> None:
        super().__init__(rundir)
        self.node_results : dict[Path, pd.DataFrame] = {}

    @classmethod
    def getParserWildcards(cls) -> list[str]:
        return super().getParserWildcards() + ["*.mem"]

    def parse(self) -> None:
        super().parse()
        for f in self.rundir.glob("*.mem"):
            self._dbg("Parsing", f.name)
            self.node_results[f] = self.get_mem_data(f)

    @staticmethod
    def get_mem_data(fPath: Path, samp_time:int = 1, swap: bool=False) -> pd.DataFrame:
        data, timing = [], 0
        with open(fPath, mode='r') as mem_file:
            for line in mem_file.readlines():
                if "Mem: " in line:
                    data.append([timing] + line.split()[1:])
                    timing+=samp_time
                if swap and "Swap: " in line:
                    data[-1].extend(line.split()[1:])

        COLS_MEM = ["timing","total","used","free","shared","buff/cache","available"]
        COLS_SWP = ["total_swap", "used_swap", "free_swap"]
        cols = COLS_MEM if not swap else COLS_MEM + COLS_SWP
        df = pd.DataFrame(columns=cols, data=data).astype(int)
        #df["timing"] = df["timing"].astype(str)
        return df
