
from utils.utils_controllers import metaAbstractClass
from pathlib import Path
import pandas as pd
from abc import abstractmethod

class AbstractParser(metaAbstractClass):

    def __init__(self, rundir: Path) -> None:
        self.results: dict[str, pd.DataFrame] = {}
        self.rundir : Path = rundir

    def get_rundir(self): return self.rundir

    @classmethod
    def getParserFiles(cls) -> list[str]:
        """Files required by the parser"""
        return []

    @classmethod
    def getParserWildcards(cls) -> list[str]:
        return []

    def avail_results(self) -> list[str]:
        """Check which results are available at the given rundir"""
        return []

    @abstractmethod
    def parse(self) -> None:
        """Compute the results of the rundir"""

    def get_results(self, k) -> pd.DataFrame:
        """Retrive the results for the given key"""
        if k not in self.results:
            self._err("Unable to find key", k, "@", self.rundir)
            return None
        return self.results[k]


    def _add_result(self, result_key:str, data: dict|pd.DataFrame):
        if result_key in self.results:
            self._warn("Updating results for", result_key)
        if isinstance(data, pd.DataFrame):
            self.results[result_key] = data
        elif isinstance(data, dict):
            self.results[result_key] = pd.DataFrame([data])
        else:
            raise TypeError("Invalid type @ _add_result")
