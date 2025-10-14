from pandas.core.internals.array_manager import itertools
from perfLens.parsers.AbstractParser import AbstractParser

from utils.utils_controllers import metaAbstractClass
from utils.utils_files import explore_fldr
from utils.utils_py import pathfy
from utils.utils_py import stringfy

import pandas as pd

from pathlib import Path
from typing import Type, Dict



_ANALYZER_REGISTRY: dict[str, Type[AbstractParser]] = {}

def register_parser(cls: Type[AbstractParser]):
    if not issubclass(cls, AbstractParser):
        raise TypeError(f"{cls.__name__} is not a subclass of AbstractParser")

    name = str.lower(cls.__name__)
    if name in _ANALYZER_REGISTRY:
        raise ValueError(f"Analyzer '{name}' is already used!")

    _ANALYZER_REGISTRY[name] = cls
    return cls


class ParserManager(metaAbstractClass):
    def __init__(self, mode : str) -> None:
        self.mode = mode
        if not mode in _ANALYZER_REGISTRY:
            raise Exception(f"Invalid parser {mode}")
        self.mode_class = _ANALYZER_REGISTRY[self.mode]
        #self.parsers : dict[str, AbstractParser] = dict()
        self.parsers : list[AbstractParser] = []
        self.agg_results :dict[str, pd.DataFrame] = dict()
        self._info("Using mode", mode)

    def add_inputs(self, rundirs: list[str]):
        self.parsers += [self.mode_class(pathfy(r)) for r in rundirs]

    def explore(self, root_rundir: Path|str):
        """Append data from root_rundirs"""
        for f in self.mode_class.getParserFiles():
             self._dbg("Searching for", f)
             self.add_inputs(explore_fldr(Path(root_rundir), f))


    def list_results(self) -> list[str]:
        for parser in self.parsers:
            print(parser.get_rundir(), "->:", stringfy(parser.avail_results()))

    def parse(self) -> None:
        _ = [p.parse() for p in self.parsers]

    def show_results(self, keys: str|list[str]):
        for k in keys:
            print("Showing results for", k, "...")
            dfs = [p.get_results(k) for p in self.parsers]
            if len(dfs) == 0 or all(x is None for x in dfs):
                self._warn("Unable to find any result for", k)
                continue
            self.agg_results[k] = pd.concat(dfs, ignore_index=True)
            print(self.agg_results[k])

    def list_paths(self) -> list[str]:
        return [p.get_rundir() for p in self.parsers]

    @staticmethod
    def available() -> list[str]:
        return list(_ANALYZER_REGISTRY.keys())
