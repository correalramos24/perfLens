
from utils.utils_controllers import metaAbstractClass
import pandas as pd

class AbstractParser(metaAbstractClass):

    def __init__(self) -> None:
        self.results: dict[str, pd.DataFrame] = {}

    @classmethod
    def analyzerFiles(cls):
        return []

    @classmethod
    def avail_results(cls):
        return []

    def get_results(self, results_key) -> pd.DataFrame:
        return self.results[results_key]
