
from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser

import pandas as pd
from pathlib import Path
import re

@register_parser
class PidstatParser(AbstractParser):
    LOG_EXTENSION = "pstat"
    CPU_INFO = {'Timestamp': 'str','UID': 'int', 'PID': 'int',
        '%usr': 'float', '%system': 'float', '%guest': 'float',
        '%wait': 'float', '%CPU': 'float','CPU': 'int','Command': 'str'
    }

    def __init__(self, rundir: Path) -> None:
        super().__init__(rundir)

    @classmethod
    def getParserWildcards(cls) -> list[str]:
        return super().getParserWildcards() + [f"*.{cls.LOG_EXTENSION}"]

    def avail_results(self) -> list[str]:
        ret = super().avail_results()
        ret.extend([f.name for f in self.rundir.glob(f"*.{self.LOG_EXTENSION}")])
        return ret

    def parse(self) -> None:
        super().parse()
        for f in self.rundir.glob(f"*.{self.LOG_EXTENSION}"):
            self._dbg("Parsing", f.name)
            self._add_result(f.name, self.get_pidstat_data_cpu(f))

    @staticmethod
    def get_pidstat_data_cpu(fPath: Path) -> pd.DataFrame:
        data = PidstatParser.__gather_pidstat_data(fPath)
        df = pd.DataFrame(data, columns=list(PidstatParser.CPU_INFO.keys()))
        df.astype(PidstatParser.CPU_INFO)
        return df

    @staticmethod
    def get_pidstat_data_io() -> pd.DataFrame:
        raise Exception("Not implemented yet!")

    @staticmethod
    def __gather_pidstat_data(fPath: Path) -> list[str]:
        ret = []
        with open(fPath, mode="r") as pidstat_file:
            for line in pidstat_file.readlines():
                if "CPU)" in line:  # Get Number of CPUS
                    match = re.search(r'\((\d+) CPU\)', line)
                    num_cpus = int(match.group(1)) if match else None
                    continue
                if line.strip() == '' or "PID" in line: #Header or empty line!
                    continue
                if line.startswith("Average:"):  # Found average => END
                    break
                ret.append(line.split())
        return ret
