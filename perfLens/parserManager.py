from perfLens.parsers.AbstractParser import AbstractParser

from utils.utils_controllers import metaAbstractClass

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
    analyzers : dict[str, AbstractParser] = dict()

    def __init__(self, mode : str) -> None:
        self.mode = mode
        self.results : dict[str, AbstractParser] = dict()
        self._info("Using mode", mode)

    def explore(self):
        ret = set()


        return ret

    def parse(self, inputs) -> None:
        pass

    def list_results(self, inputs) -> list[str]:
        return None

    def show_results(self, keys: str|list[str]):
        pass

    @staticmethod
    def available() -> list[str]:
        return list(_ANALYZER_REGISTRY.keys())
