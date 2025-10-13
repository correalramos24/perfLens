
from perfLens.parsers.AbstractParser import AbstractParser
from perfLens.parserManager import register_parser

@register_parser
class EnvParser(AbstractParser):
    def __init__(self):
        super().__init__()
